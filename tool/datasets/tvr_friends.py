"""
This file contains code for upload and retrieve moments for a given dataset
It generates the result file for eval code to use.
This code is yet to be pollished.
"""
import json
from operator import length_hint
import pysrt
import pandas as pd

from io import BytesIO
from PIL import Image
from os import path
import os

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from core import UploadPipeline, RetrievalPipeline
from core.module.vectorizer import CLIPVectorizer
from core.utils import video_processing
from tool.utils import load_jsonl, write_jsonl

class TVRFriendsDataset():
    def __init__(self, data_dir,
            clip_name="ViT-B/16",
        ) -> None:
        """each clip is a moment"""
        # data = load_jsonl(file_path)
        
        # self.data_df = pd.DataFrame(data)
        self.subtitles_dir = f"{data_dir}/subtitles"
        self.frames_dir = f"{data_dir}/frames"
        self.moment_names = os.listdir(self.frames_dir)
        self.moment_names.sort(key=lambda name: int(name.split('_')[-1])) 
               
        self.frame_vectorizer = CLIPVectorizer(clip_name)
        self.moment_vectorizer = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

        # self.moment_names = 
        
    def upload(self, moment_table, frame_table):
        up = UploadPipeline(moment_table, frame_table)

        uploaded_video = len(self.data_df)
        for i, moment_name in enumerate(self.moment_names):
            moment_dir = os.join(self.frames_dir, moment_name)
            
            subtitle_path = os.join(self.subtitles_dir, f"{moment_name}.srt") 
            assert os.path.exists(subtitle_path)
            subs = pysrt.open(subtitle_path)
            
            frames = []
            prev_timestamp = 0.0
            for j, frame in enumerate(os.listdir(moment_dir)):
                if j%3 != 0:
                    # skip as 3fps frames
                    continue
                
                frame_path = os.join(moment_dir, f"{frame}.jpg")
                frames.append(Image.open(frame_path))
            length = j//3
             
            moment_vector = self.vectorize_subtitles(subs.text)
            frame_vectors = self.vectorize_frames(frames) 
            
            ### insert moment
            res = self.db.insert(self.moment_table, {
                "name": moment_name,       # output_dir/$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4 -> $VIDEO_NAME-Scene-$SCENE_NUMBER
                "timestamp": [prev_timestamp, length],
                "vector": moment_vector.tolist()       # type: ignore
                "subtitles": subs.text 
            })
            prev_timestamp = length
            moment_id = res.data[0]["id"]  

            for j, vector in enumerate(frame_vectors):
                frame = video_processing.encode_img_to_base64(frames[j]).decode("utf-8")
                    
                res = self.db.insert(self.frame_table, {
                    "moment_id": moment_id,
                    "frame_base64": frame,           # need to turn byte to str, as JSON only accept str
                    "vector": vector.tolist(),                              # jsn only support list
                })
                
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
    
    def vectorize_query(self, query):
        return self.moment_vectorizer.encode(
            query,
            prompt="query:",
            convert_to_tensor=True
        )
        
    def vectorize_subtitles(self, raw_subtitles):
        return self.moment_vectorizer.encode(
            raw_subtitles, 
            prompt="One day in the Firends TV show, the main charaters are having a conversation. \ndialog:",
            convert_to_tensor=True
        )
        
if __name__ == "__main__":
    friends = TVRFriendsDataset("/csproject/dan3/data/tvqa/friends_s01e05")   
    friends.upload(
        moment_table="tvr_friends_moments_0416",
        frame_table="tvr_friends_frames_0416"
    )
        