from typing import List

from .vec_db import PgvectorDB
from .module.vectorizer import CLIPVectorizer
from .module.segmenter import ShotDetectSegmenter

class RetrievalPipeline:
    db = PgvectorDB(
        server_url="localhost",
        pwd="password"
    )
    vectorizer = CLIPVectorizer()
    
    def retrive_moment_ids(self, prompt: str, k=5):
        query_vec = self.vectorizer.vectorize_txt(prompt)
        
        return self.db.fetch_moment_id_by_vector(
            "qvhiglight_clip_moment_vector_0209",
            query_vec
            )                        # [(id, dist)]

    def retrieve_moments(self, prompt: str, k=5, video_name=None) -> dict:
        """ return [moment_id, video_name,  timestamp, cos_dist)] """
        query_vec = self.vectorizer.vectorize_txt(prompt)
        if video_name is None:
            moments = self.db.fetch_moments_by_vector(
                vector_table_name="qvhiglight_clip_moment_vector_0209",
                moment_table_name="qvhiglight_clip_moment_0209",
                input_vector=query_vec
            )       # 
        else:
            moments = self.db.fetch_moments_by_vector_and_name(
                vector_table_name="qvhiglight_clip_moment_vector_0209",
                moment_table_name="qvhiglight_clip_moment_0209",
                input_vector=query_vec,
                video_name=video_name
            )       # 
            
        
        return moments
    
        
    def get_video_id(self, video_name: str):
        return ShotDetectSegmenter.parse_video_name(video_name)
        
        
        