import json
from io import BytesIO

def load_jsonl(file_path):
    with open(file_path, "rb") as f:
        for line in f.readlines():
            yield json.loads(line)
            
def upload_video_from_dataset(file_path):
    vids = {data["vid"] for data in load_jsonl(file_path)}   # use set to avoid repeat
    
    for vid in vids:
        ## insert each video
        ...
    
    