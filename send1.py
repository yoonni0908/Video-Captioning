import os
import subprocess
import json
import websocket
import ast
import re
import argparse

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8')

def run_command1(command):
    VGGISH_PYTHON_PATH = "/home/ubuntu/anaconda3/envs/vggish/bin/python"
    if command.startswith("python "):
        command = VGGISH_PYTHON_PATH + command[6: ]
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8')


def extract_captions_from_output(output):
    # 결과에서 JSON 부분만 추출
    start_index = output.find("[{")
    end_index = output.find("}]") + 2
    json_str = output[start_index:end_index]

    # JSON 문자열을 파싱
    captions = eval(json_str)

    # 각 사전에서 'sentence' 키의 값을 추출
    #sentences = [caption_dict['sentence'] for caption_dict in captions]

    sentence_choose = captions[5]['sentence']

    # 모든 문장을 하나의 문자열로 결합
    #final_caption = " ".join(sentences)

    return sentence_choose

def get_base_name(video_path):
    
    return os.path.splitext(os.path.basename(video_path))[0]

def parse_args():
    parser = argparse.ArgumentParser(description = "Process video for captioning.")
    parser.add_argument('--video_paths', type=str, required=True, help='Path to the video file.')
    return parser.parse_args()

# get command-line arguments
args = parse_args()

video_path = args.video_paths
base_name = get_base_name(video_path)
print(base_name)
i3d_output_path = f"../../test/"
vggish_output_path = f"../../test/"
vggish_feature_path = f"./test/{base_name}_vggish.npy"
rgb_feature_path = f"./test/{base_name}_rgb.npy"
flow_feature_path = f"./test/{base_name}_flow.npy"

# Extract I3D features
os.chdir('./submodules/video_features')
#run_command('conda env create -f conda_env_i3d.yml')
run_command('conda deactivate')
run_command('conda activate i3d')
# stdout, stderr = run_command('python main.py --feature_type i3d --on_extraction save_numpy --device_ids 0 --extraction_fps 25 --video_paths ../../sample/women_long_jump.mp4 --output_path ../../sample/')

stdout, stderr = run_command(f'python main.py --feature_type i3d --on_extraction save_numpy --device_ids 0 --extraction_fps 25 --video_paths {"../../"+video_path} --output_path {i3d_output_path}')

print("STDOUT:", stdout)
print("STDERR:", stderr)

# Extract vggish feature
#run_command('conda env create -f conda_env_vggish.yml')

run_command1('conda deactiavte')
run_command1('source /home/ubuntu/anaconda3/etc/profile.d/conda.sh && conda activate vggish')
#stdout, stderr = run_command1('python main.py --feature_type vggish --on_extraction save_numpy --device_ids 0 --extraction_fps 25 --video_paths ../../sample/women_long_jump.mp4 --output_path ../../sample/')
stdout, stderr = run_command1(f'python main.py --feature_type vggish --on_extraction save_numpy --device_ids 0 --extraction_fps 25 --video_paths {"../../"+video_path} --output_path {vggish_output_path}')

print("STDOUT:", stdout)
print("STDERR:", stderr)

# Finally captioning based on the 3 saved features
os.chdir('../../')
run_command('conda deactivate')
run_command('conda activate bmt')

# stdout, stderr = run_command('python ./sample/single_video_prediction.py --prop_generator_model_path ./sample/best_prop_model.pt --pretrained_cap_model_path ./sample/best_cap_model.pt --vggish_features_path sample/women_long_jump_vggish.npy --rgb_features_path sample/women_long_jump_rgb.npy --flow_features_path sample/women_long_jump_flow.npy --duration_in_secs 99 --device_id 0 --max_prop_per_vid 100 --nms_tiou_thresh 0.4')
stdout, stderr = run_command(f'python ./sample/single_video_prediction.py --prop_generator_model_path ./sample/best_prop_model.pt --pretrained_cap_model_path ./sample/best_cap_model.pt --vggish_features_path {vggish_feature_path} --rgb_features_path {rgb_feature_path} --flow_features_path {flow_feature_path} --duration_in_secs 10 --device_id 0 --max_prop_per_vid 100 --nms_tiou_thresh 0.4')
print("STDOUT:", stdout)
print("STDERR:", stderr)

caption = extract_captions_from_output(stdout)


# Display the captioning result
print("Captioning Result:", caption)

# Send captioned data to the server as a file in json format via websocket
data = {
    "sender": "AI",
    "data": {
        "caption": caption
    }
}

# TODO: Connect to the appropriate websocket server and send the data.
ws = websocket.WebSocket()
print(type(data))
print(data['data'])
ws.connect("ws://117.16.137.205:8080/ai")
ws.send(json.dumps(data))
ws.close()
