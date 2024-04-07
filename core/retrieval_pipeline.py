from typing import List

from .vec_db import PgvectorDB
from .vec_db import SupabaseDB
from .module.vectorizer import CLIPVectorizer
from .module.segmenter import ShotDetectSegmenter

class RetrievalPipeline:
    db = PgvectorDB(
        server_url="localhost",
        pwd="password"
    )
    vectorizer = CLIPVectorizer()

    supabase_db = SupabaseDB()
    
    def retrive_moment_ids(self, prompt: str, k=5):
        query_vec = self.vectorizer.vectorize_txt(prompt)
        
        return self.db.fetch_moment_id_by_vector(
            "qvhiglight_clip_moment_vector_0209",
            query_vec
            )                        # [(id, dist)]

    def retrieve_moments(self, prompt: str, k=5) -> dict:
        """ return [(moment_id, video_name, timestamp, cos_dist, frame_ids)] """
        query_vec = self.vectorizer.vectorize_txt(prompt)

        # retrieve k moments
        moments = self.db.fetch_moments_by_vector(
            vector_table_name="qvhiglight_clip_moment_vector_0209",
            moment_table_name="qvhiglight_clip_moment_0209",
            input_vector=query_vec,
            k=k
        )      
        
        return moments
    
    def retrieve_moments_by_video_id(self, video_id: str, prompt: str, k=5) -> dict:
        query_vec = self.vectorizer.vectorize_txt(prompt)

        # retrieve k moments
        moments = self.db.fetch_moments_by_vector_with_video_id(
            video_id=video_id,
            vector_table_name="qvhiglight_clip_moment_vector_0209",
            moment_table_name="qvhiglight_clip_moment_0209",
            input_vector=query_vec,
            k=k
        )      
        
        return moments
    
        
    def get_video_id(self, video_name: str):
        return ShotDetectSegmenter.parse_video_name(video_name)

    def retrieve_base64_by_ids(self, ids: List[int]):
        return self.supabase_db.fetch_base64_by_ids("qvhiglight_clip_moment_vector_0209", ids)
        
        
        