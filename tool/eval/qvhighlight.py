import json

from io import BytesIO
from os import path

from core import UploadPipeline, RetrievalPipeline

def load_jsonl(file_path):
    with open(file_path, "rb") as f:
        for line in f.readlines():
            yield json.loads(line)
            
def upload_video_from_dataset(file_path, video_path):
    up = UploadPipeline(
        moment_table_name="moment_test",
        vector_table_name="moment_feature_test"
    )
    vids = {data["vid"] for data in load_jsonl(file_path)}   # use set to avoid repeat
    
    for vid in vids:
        ## insert each video
        print(vid)
        video_path = path.join(video_path, f"{vid}.mp4")        # aware of .avi
        up.upload_video_file(video_path)
        break
    
def test_retrieval(prompt):
    rp = RetrievalPipeline()
    print(rp.retrive(str(prompt)))
    
if __name__ == "__main__":
    print("hi")
    DATA_PATH = "/data/ptpyip/downloads/datasets/qvhilights"
    # upload_video_from_dataset(f"{DATA_PATH}/highlight_val_release.jsonl", f"{DATA_PATH}/videos")
    test_retrieval("Police in riot gear are marching down the street.")
    
    