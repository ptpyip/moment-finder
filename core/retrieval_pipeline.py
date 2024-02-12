from .vec_db import PgvectorDB
from .module.vectorizer import CLIPVectorizer

class RetrievalPipeline:
    db = PgvectorDB(
        server_url="localhost",
        pwd="password"
    )
    vectorizer = CLIPVectorizer()
    
    def retrive_moment_ids(self, prompt: str, k=5) -> list[int, float]:
        query_vec = self.vectorizer.vectorize_txt(prompt)
        
        return self.db.fetch_moment_id_by_vector(
            "qvhiglight_clip_moment_vector_0209",
            query_vec
            )                        # [(id, dist)]

    def retrive_moments(self, prompt: str, k=5):
        query_vec = self.vectorizer.vectorize_txt(prompt)
        
        moments = self.db.fetch_moments_by_vector(
            vector_table_name="qvhiglight_clip_moment_vector_0209",
            moment_table_name="qvhiglight_clip_moment_0209",
            input_vector=query_vec
        ) 
        
        moment_scores = {
            moment_id: 1 - distance for moment_id, distance in moments
        }
        
        
        