"""
This file contains code for upload and retrieve moments for a given dataset
It generates the result file for eval code to use.
This code is yet to be pollished.
"""
import json
import pysrt
import pandas as pd

from io import BytesIO
from os import path
import os

from core import UploadPipeline, RetrievalPipeline
from tool.utils import load_jsonl, write_jsonl

class TVRFriendsDataset():
    def __init__(self, data_dir, frames_dir) -> None:
        """each clip is a moment"""
        # data = load_jsonl(file_path)
        
        # self.data_df = pd.DataFrame(data)
        self.frames_dir = f"{data_dir}/frames"
        self.moment_names = os.listdir(self.frames_dir)
        # self.moment_names = 
        
    def upload(self, moment_table, frame_table):
        up = UploadPipeline(moment_table, frame_table)

        uploaded_video = len(self.data_df)
        for moment_name in self.moment_names:
            
            video_path = path.join(self.video_dir, f"{vid}.mp4")        # aware of .avi
            
            if not path.exists(video_path):
                uploaded_video -= 1
                print(f"video does not exixt: {video_path}")
                continue
            else:
                up.upload_video_file(video_path) 
                
        return uploaded_video
    
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
        
        