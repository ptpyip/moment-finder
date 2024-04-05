"""
This file contains code for upload and retrieve moments for a given dataset
It generates the result file for eval code to use.
This code is yet to be pollished.
"""
import json

from io import BytesIO
from os import path

from core import UploadPipeline, RetrievalPipeline

def load_jsonl(file_path):
    with open(file_path, "rb") as f:
        for line in f.readlines():
            yield json.loads(line)
            
def write_jsonl(dict_list, out_dir, file_name):
     with open(path.join(out_dir, f"{file_name}.jsonl"), 'w') as out:
        for data in dict_list:
            josn_data = json.dumps(data) + '\n'
            out.write(josn_data)
            
def upload_video_from_dataset(
        file_path, video_dir,
        moment_table_name="qvhiglight_clip_moment_0209",
        vector_table_name="qvhiglight_clip_moment_vector_0209",
        use_moment_vector=False, upload_frame=True
    ):
    up = UploadPipeline(moment_table_name, vector_table_name, use_moment_vector, upload_frame)
    vids = {data["vid"] for data in load_jsonl(file_path)}   # use set to avoid repeat
    
    for vid in vids:
        ## insert each video
        print(vid)
        
        video_path = path.join(video_dir, f"{vid}.mp4")        # aware of .avi
        if not path.exists(path.join(file_path, video_path)):
            print(f"video does not exixt: {path.join(file_path, video_path)}")
            continue
        
        up.upload_video_file(video_path)
        # break

def retrieve_video_using_dataset_prompt(file_path, k=5):
    # DATASET_PATH = "/home/ptpyip/fyp/datasets/qvhilights/highlight_val_release.jsonl"
    
    rp = RetrievalPipeline()

    result = []
    for data in load_jsonl(file_path):        
        retrieval_result = rp.retrieve_moments(data.get("query"), k=5)
        
        pred_relevant_windows = []
        for moment_id, video_name, timestamp, cos_dist in retrieval_result:
            pred_vid = rp.get_video_id(video_name)
            print(pred_vid)
            if pred_vid == data.get("vid"):
                pred_relevant_windows.append(
                    [*timestamp, 1 - cos_dist]
                )
        
                
        print(f"query: {data.get('qid')} has {len(pred_relevant_windows)} result")
        result.append({
            "qid": data.get("qid"),
            "query": data.get("query"),
            "vid":  data.get("vid"),
            "pred_relevant_windows": pred_relevant_windows            
        }) 
          
    
    write_jsonl(result, "/home/ptpyip/fyp", "out")  
        
    
def test_retrieval(prompt):
    rp = RetrievalPipeline()
    print(rp.retrive(str(prompt)))
    
if __name__ == "__main__":
    DATA_PATH = "/csproject/dan3/data/qvhiglights/"
    import argparse

    parser = argparse.ArgumentParser("Test Upload Pipeline")
    parser.add_argument("--moment-table", type=str)
    parser.add_argument("--vector-table", type=str)
    parser.add_argument("--use-moment-vector", action='store_true')
    parser.add_argument("--video", type=str)
    parser.add_argument("--source-dir", type=str, default=DATA_PATH)
    args = parser.parse_args()
    
    upload_video_from_dataset(
        file_path=f"{args.source_dir}/highlight_val_release.jsonl", 
        video_dir=f"{args.source_dir}/videos",
        moment_table_name=args.moment_table,
        vector_table_name=args.vector_table
    )
    # # test_retrieval("Police in riot gear are marching down the street.")
    # retrieve_video_using_dataset_prompt(f"{DATA_PATH}/highlight_val_release.jsonl")
        
    print("success")
    
    