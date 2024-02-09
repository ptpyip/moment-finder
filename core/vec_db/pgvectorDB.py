# import vecs as pgvector

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_pg_db_url(server_url, port_num, db_name, user_name, pwd):
    return f"postgresql://{user_name}:{pwd}@{server_url}:{port_num}/{db_name}" 

class PgvectorDB: 
    PG_DB_CONNECTION = "postgresql://postgres.augwkisabfpevnwvzzqu:password_test_123123@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    # import torch
    # torch.Tensor.squeeze
    
    def __init__(self, 
        server_url = "db.augwkisabfpevnwvzzqu.supabase.co", 
        port_num = 5432, db_name = "postgres", 
        user_name = "postgres", pwd="password_test_123123"
    ) -> None:
        # self.PG_DB_CONNECTION = get_pg_db_url(server_url, port_num, db_name, user_name, pwd)
        self.engine = create_engine(self.PG_DB_CONNECTION)
        self.Session = sessionmaker(self.engine)
    def fetch_features_by_vector(self, input_vector, k=5, return_frame=False):
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT id AS feature_id, moment_id,{' frame_base64,' if return_frame else ''} vector <-> '{input_vector.squeeze().tolist()}' AS distance
                FROM moment_feature_test 
                ORDER BY distance LIMIT {int(k)};"""
                # WHERE vector <-> '{input_vector.tolist()}' < {distance}"""
            )).fetchall()

        
    def fetch_moment_by_vector(self, input_vector, k=5, return_frame_count=False):
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT moment_id,
                    {' COUNT(*) AS number_of_frame,' if return_frame_count else ''} 
                    max(vector <-> '{input_vector.squeeze().tolist()}') AS distance
                FROM moment_feature_test
                group by moment_id 
                ORDER BY distance LIMIT {int(k)};"""
            )).fetchall()

    def test_connection(self):
        with self.Section() as session:
            return session.execute(text(f"""
                SELECT *
                FROM items 
            """)).fetchall()