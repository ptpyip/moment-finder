# import vecs as pgvector

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DatabaseError

def get_pg_db_url(server_url, port_num, db_name, user_name, pwd):
    return f"postgresql://{user_name}:{pwd}@{server_url}:{port_num}/{db_name}" 

class PgvectorDB: 
    PG_DB_CONNECTION = "postgresql://postgres.augwkisabfpevnwvzzqu:password_test_123123@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    # import torch
    # torch.Tensor.squeeze
    
    def __init__(self, 
        server_url = "localhost", 
        port_num = 5432, db_name = "postgres", 
        user_name = "postgres", pwd="password"
    ):
        self.PG_DB_CONNECTION = get_pg_db_url(server_url, port_num, db_name, user_name, pwd)
        self.engine = create_engine(self.PG_DB_CONNECTION)
        self.Session = sessionmaker(self.engine)
        
        assert self.test_connection_success()
    

    def fetch_moments_by_vector_v2(self, moment_table_name: str, input_vector, video_name=None, k=5):
        ## validate table_name
        
        with self.Session() as session:
            return session.execute(text(f"""
                SET LOCAL hnsw.ef_search = 100;
                SELECT id, name, timestamp,
                    vector <=> '{input_vector.squeeze().tolist()}' AS distance         
                FROM {moment_table_name}
                {f'WHERE name LIKE {video_name}' if video_name is not None else ''}
                ORDER BY distance limit {k}
            """)).fetchall()

        
    # def set_VMR_table(self, moment_table_name, )

    def fetch_moments_by_vector(self, vector_table_name:str, moment_table_name: str, input_vector, k=5):
        ## validate table_name
        
        with self.Session() as session:
            
            return session.execute(text(f"""
                SET LOCAL hnsw.ef_search = 100;
                SELECT id, name, timestamp, min_distance
                FROM {moment_table_name} AS moment_table
                    JOIN (
                        SELECT moment_id, min(distance) AS min_distance
                        FROM (
                            SELECT moment_id,
                                vector <=> '{input_vector.squeeze().tolist()}' AS distance         
                            FROM {vector_table_name}
                            ORDER BY distance limit 100
                        ) AS vector_table
                        GROUP BY moment_id       
                        ORDER BY min(distance) limit 5 
                    ) AS result_table 
                    ON result_table.moment_id = moment_table.id 
            """)).fetchall()
        
    

    def fetch_moments_by_vector_and_name(self, vector_table_name:str, moment_table_name: str, input_vector, video_name, k=5):
        ## validate table_name
        
        with self.Session() as session:
            
            return session.execute(text(f"""
                SET LOCAL hnsw.ef_search = 100;
                SELECT id, name, timestamp, min_distance
                FROM {moment_table_name} AS moment_table
                    JOIN (
                        SELECT moment_id, min(distance) AS min_distance
                        FROM (
                            SELECT moment_id,
                                vector <=> '{input_vector.squeeze().tolist()}' AS distance         
                            FROM {vector_table_name}
                            WHERE moment_id IN (
                                SELECT id
                                FROM qvhiglight_clip_moment_0209 AS moment_table
                                WHERE name LIKE '{video_name}%'
                            ) 
                            ORDER BY distance limit 100
                        ) AS vector_table
                        GROUP BY moment_id       
                        ORDER BY min(distance) limit 5 
                    ) AS result_table 
                    ON result_table.moment_id = moment_table.id 
            """)).fetchall() 
        
    def fetch_features_by_vector(self, feature_table_name:str, input_vector, k=5, return_frame=False):
        ## validate table_name
        
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT id AS feature_id, moment_id,{' frame_base64,' if return_frame else ''} vector <=> '{input_vector.squeeze().tolist()}' AS distance
                FROM {feature_table_name} 
                ORDER BY distance LIMIT {int(k)};"""
                # WHERE vector <-> '{input_vector.tolist()}' < {distance}"""
            )).fetchall()

        
    def fetch_moment_id_by_vector(self, feature_table_name:str, input_vector, k=5, return_frame_count=False):
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT moment_id,
                    {' COUNT(*) AS number_of_frame,' if return_frame_count else ''} 
                    max(vector <=> '{input_vector.squeeze().tolist()}') AS distance
                FROM {feature_table_name}
                group by moment_id 
                ORDER BY distance LIMIT {int(k)};"""
            )).fetchall()

    def fetch_moment_by_id(self, moment_table_name: str, moment_id):
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT * FROM {moment_table_name} WHERE id = {moment_id}
            """)).fetchall()
            

    def fetch_moment_by_ids(self, moment_table_name: str, moment_ids: tuple):
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT * FROM {moment_table_name} WHERE id IN {moment_ids}
            """)).fetchall()

    def test_connection(self):
        with self.Session() as session:
            return session.execute(text(f"""
                SELECT *
                FROM items 
            """)).fetchall()
            
    def test_connection_success(self):
        try:
            self.test_connection()
            return True
        except DatabaseError:
            return False
            
    