"""
This file contains code for upload and retrieve moments for a given dataset
It generates the result file for eval code to use.
This code is yet to be pollished.
"""
import json

from io import BytesIO
from os import path

from core import UploadPipeline, RetrievalPipeline
from tool.utils import load_jsonl, write_jsonl

from .eval import eval_submission
            
def upload_video_from_dataset(file_path, video_dir):
    up = UploadPipeline(
        moment_table_name="qvhiglight_clip_moment_0209",
        vector_table_name="qvhiglight_clip_moment_vector_0209"
    )
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

def retrieve_video_using_dataset_prompt(file_path, k=5, skip_not_exisit=True):
    # DATASET_PATH = "/home/ptpyip/fyp/datasets/qvhilights/highlight_val_release.jsonl"
    
    rp = RetrievalPipeline()

    gt = []
    pred = []
    for data in load_jsonl(file_path): 
        vid = data.get("vid") 
        
        retrieval_result = rp.retrieve_moments(data.get("query"), k=5, video_name=vid)
        if len(retrieval_result) == 0 and skip_not_exisit:
            # skip video does not exist.
            continue
        
        gt.append(data)
        pred_relevant_windows = []
        for moment_id, video_name, timestamp, cos_dist in retrieval_result:
            pred_vid = rp.get_video_id(video_name)
            print(pred_vid)
            if pred_vid == vid:
                pred_relevant_windows.append(
                    [*timestamp, 1 - cos_dist]
                )
        
                
        print(f"query: {data.get('qid')} has {len(pred_relevant_windows)} result")
        pred.append({
            "qid": data.get("qid"),
            "query": data.get("query"),
            "vid":  data.get("vid"),
            "pred_relevant_windows": pred_relevant_windows            
        })
        
    results = eval_submission(pred, gt) 
        
    # write_jsonl(result, "/home/ptpyip/fyp", "preds_metrics")  
    
    with open("/home/ptpyip/fyp/preds_metrics.json", "w") as f:
        f.write(json.dumps(results, indent=4))

        
    
def test_retrieval(prompt):
    rp = RetrievalPipeline()
    print(rp.retrive(str(prompt)))
    
if __name__ == "__main__":
    print("hi")
    DATA_PATH = "/home/ptpyip/fyp/datasets/qvhighlights"
    # upload_video_from_dataset(f"{DATA_PATH}/highlight_val_release.jsonl", f"{DATA_PATH}/videos")
    # test_retrieval("Police in riot gear are marching down the street.")
    retrieve_video_using_dataset_prompt(f"{DATA_PATH}/highlight_val_release.jsonl")
    
    