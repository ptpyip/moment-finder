"""
This file contains code for upload and retrieve moments for a given dataset
It generates the result file for eval code to use.
This code is yet to be pollished.
"""
import json

from io import BytesIO
from os import path

from core import UploadPipeline, RetrievalPipeline

from .eval import eval_submission

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
        frame_table_name="qvhiglight_clip_moment_vector_0209",
        use_moment_vector=False, store_frame=True
    ):
    up = UploadPipeline(
        moment_table_name, 
        frame_table_name,
        use_moment_vector=use_moment_vector, 
        store_frame=store_frame
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

def retrieve_video_using_dataset_prompt(file_path, k=5, skip_not_exisit=True, use_moment_vector=False):
    # DATASET_PATH = "/home/ptpyip/fyp/datasets/qvhilights/highlight_val_release.jsonl"
    
    rp = RetrievalPipeline()

    gt = []
    pred = []
    for data in load_jsonl(file_path): 
        vid = data.get("vid") 
        if use_moment_vector:
            retrieval_result = rp.retrieve_moments_v2(data.get("query"), k=5, video_name=vid) 
        else:
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

        
    
# def test_retrieval(prompt):
#     rp = RetrievalPipeline()
#     print(rp.retrive(str(prompt)))
    
if __name__ == "__main__":
    # print("hi")
    # DATA_PATH = "/home/ptpyip/fyp/datasets/qvhighlights"
    # DATA_PATH = "/csproject/dan3/data/qvhiglights"
    # upload_video_from_dataset(f"{DATA_PATH}/highlight_val_release.jsonl", f"{DATA_PATH}/videos")
    # test_retrieval("Police in riot gear are marching down the street.")
    import argparse

    parser = argparse.ArgumentParser("Handling qvhiglight")
    parser.add_argument("upload", action='store_true')
    parser.add_argument("--source-dir", type=str)
    parser.add_argument("--moment-table", type=str)
    parser.add_argument("--frame-table", type=str)
    parser.add_argument("--use-moment-vector", action='store_true')
    # TODO:
    # parser.add_argument("--config", type=str)
    args = parser.parse_args()
    if args.upload:
        
        upload_video_from_dataset(
            file_path=f"{args.source_dir}/highlight_val_release.jsonl", 
            video_dir=f"{args.source_dir}/videos",
            moment_table_name=args.moment_table,
            frame_table_name=args.frame_table,
            use_moment_vector=args.use_moment_vector
        )
    else:
    # # test_retrieval("Police in riot gear are marching down the street.")
        retrieve_video_using_dataset_prompt(f"{args.source_dir}/highlight_val_release.jsonl", use_moment_vector=args.use_moment_vector)
        
    print("success")
    
    