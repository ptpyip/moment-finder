
from .vec_db import PgvectorDB
from .module.vectorizer import CLIPVectorizer

class RetrievalPipeline:
    db = PgvectorDB()
    vectorizer = CLIPVectorizer()
    
    def retrive(self, prompt: str, k=5):
        query_vec = self.vectorizer.vectorize_txt(prompt)
        
        return self.db.fetch_moment_by_vector(query_vec)