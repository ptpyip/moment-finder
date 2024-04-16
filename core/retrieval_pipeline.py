from typing import List

from .vec_db import PgvectorDB
from .module.vectorizer import CLIPVectorizer, CLIP4ClipVectorizer, CLIP4ClipVectorizerV2
from .module.segmenter import ShotDetectSegmenter

class RetrievalPipeline:
    def __init__(self,
        # moment_table, frame_table,
        clip_name="ViT-B/32",
        clip4clip_name="meanP-ViT-B/16",
        clip4clip_path="/csproject/dan3/downloads/ckpts/meanP-ViT-B-16.bin.3",
        serverl_url="localhost", use_moment_vector = False 
    ) -> None:
        self.use_moment_vector = use_moment_vector
        
        self.vec_db = PgvectorDB(serverl_url)
        self.txt2frame_vectorizer = CLIPVectorizer(clip_name)

        # self.txt2moment_vectorier = CLIP4ClipVectorizerV2() if use_moment_vector else None
        self.txt2moment_vectorier = CLIP4ClipVectorizer(
           clip4clip_name, clip4clip_path
        ) if use_moment_vector else None
                 # [(id, dist)]

    def retrieve_moments(self, prompt: str, k=5, video_name=None) -> dict:
        """ return [moment_id, video_name,  timestamp, cos_dist)] """
        query_vec = self.txt2frame_vectorizer.vectorize_txt(prompt)
        if video_name is None:
            moments = self.vec_db.fetch_moments_by_vector(
                vector_table_name="qvhiglight_clip_moment_vector_0209",
                moment_table_name="qvhiglight_clip_moment_0209",
                input_vector=query_vec
            )       # 
        else:
            moments = self.vec_db.fetch_moments_by_vector_and_name(
                vector_table_name="qvhiglight_clip_moment_vector_0209",
                moment_table_name="qvhiglight_clip_moment_0209",
                input_vector=query_vec,
                video_name=video_name
            )       # 
            
        
        return moments
    
        
    def get_video_id(self, video_name: str):
        return ShotDetectSegmenter.parse_video_name(video_name)
    

    def retrieve_moments_v2(self, moment_table, prompt: str, video_name=None, k=5):
        """ return [moment_id, video_name,  timestamp, cos_dist)] """
        query_vec = self.txt2moment_vectorier.vectorize_txt(prompt)
        
        moments = self.vec_db.fetch_moments_by_vector_v2(
            moment_table_name=moment_table,
            input_vector=query_vec,
            video_name=video_name
        )        
        
        return moments 
        