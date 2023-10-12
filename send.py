#!/usr/bin/env python3
import os
import subprocess
import json
import websocket

I3D_PYTHON_PATH = "/home/ubuntu/anaconda3/envs/i3d/bin/python"
VGGISH_PYTHON_PATH = "/home/ubuntu/anaconda3/envs/vggish/bin/python"
BMT_PYTHON_PATH = "/home/ubuntu/anaconda3/envs/bmt/bin/python"

def extract_i3d_features(video_path, output_path):
    os.chdir('./submodules/video_features')
    subprocess.run([I3D_PYTHON_PATH, 'main.py', '--feature_type', 'i3d', '--on_extraction', 'save_numpy', '--device_ids', '0', '--extraction_fps', '25', '--video_paths', video_path, '--output_path', output_path], shell=True)

def extract_vggish_features(video_path, output_path):
    subprocess.run([VGGISH_PYTHON_PATH, 'main.py', '--feature_type', 'vggish', '--on_extraction', 'save_numpy', '--device_ids', '0', '--extraction_fps', '25', '--video_paths', video_path, '--output_path', output_path], shell=True)

def generate_caption(vggish_features_path, rgb_features_path, flow_features_path):
    os.chdir('../../')
    result = subprocess.run([BMT_PYTHON_PATH, './sample/single_video_prediction.py', '--prop_generator_model_path', './sample/best_prop_model.pt', '--pretrained_cap_model_path', './sample/best_cap_model.pt', '--vggish_features_path', vggish_features_path, '--rgb_features_path', rgb_features_path, '--flow_features_path', flow_features_path, '--duration_in_secs', '99', '--device_id', '0', '—max_prop_per_vid', '100', '--nms_tiou_thresh', '0.4'], shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def send_caption_to_server(caption):
    data = {
        "sender": "AI",
        "data": {
            "caption": caption
        }
    }
    ws = websocket.create_connection("websocket_url(뭐임?)")
    ws.send(json.dumps(data))
    ws.close()

if __name__ == "__main__":
    video_path = "../../sample/women_long_jump.mp4"
    i3d_output_path = "../../sample/"
    vggish_output_path = "../../sample/"

    extract_i3d_features(video_path, i3d_output_path)
    extract_vggish_features(video_path, vggish_output_path)
    caption = generate_caption(vggish_features_path, rgb_features_path, flow_features_path)
    send_caption_to_server(caption)
