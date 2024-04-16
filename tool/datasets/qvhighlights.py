"""
This file contains code for upload and retrieve moments for a given dataset
It generates the result file for eval code to use.
This code is yet to be pollished.
"""
import json
import pandas as pd

from io import BytesIO
from os import path

from core import UploadPipeline, RetrievalPipeline
from tool.utils import load_jsonl, write_jsonl

class QVHighlightsDataset():
    def __init__(self, file_path, video_dir) -> None:
        data = load_jsonl(file_path)
        
        self.data_df = pd.DataFrame(data)
        self.video_dir = video_dir
        
    def upload(self, moment_table, frame_table, use_moment_vector):
        up = UploadPipeline(moment_table, frame_table, use_moment_vector, store_frame=False)

        num_uploaded_video = len(self.data_df)
        for vid in self.data_df.get("vid"):
            video_path = path.join(self.video_dir, f"{vid}.mp4")        # aware of .avi
            
            if not path.exists(video_path):
                num_uploaded_video -= 1
                print(f"video does not exixt: {video_path}")
                continue
            else:
                up.upload_video_file(video_path) 
                
        return num_uploaded_video
    
    def retrieve(self, skip_not_exisit=True, vid_is_given=False, verbose=False):
        rp = RetrievalPipeline()

        gt, pred = [], []
        for i, data in self.data_df.iterrows(): 
            vid = data.get("vid") 
            
            retrieval_result = rp.retrieve_moments(
                data.get("query"), 
                video_name=vid if vid_is_given else None,
                k=5
            )
            if len(retrieval_result) == 0 and skip_not_exisit:
                # skip video does not exist.
                continue
            
            gt.append(data)
            pred_relevant_windows = []
            for moment_id, video_name, timestamp, cos_dist in retrieval_result:
                pred_vid = rp.get_video_id(video_name)
                # print(pred_vid)
                if pred_vid == vid:
                    pred_relevant_windows.append(
                        [*timestamp, 1 - cos_dist]
                    )
            if verbose:                
                print(f"query: {data.get('qid')} has {len(pred_relevant_windows)} result")
                
            pred.append({
                "qid": data.get("qid"),
                "query": data.get("query"),
                "vid":  data.get("vid"),
                "pred_relevant_windows": pred_relevant_windows            
            })
            
        return gt, pred
        
        