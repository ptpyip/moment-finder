from supabase import create_client, Client

class SupabaseDB:
    SERVER_URL = "http://vml1wk132.cse.ust.hk:8080"
    KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"

    # TODO: get them trough env or input args
    
    
    supabase_client: Client
    
    def __init__(self, server_url=None, key=None) -> None:
        self.server_url = server_url if server_url else self.SERVER_URL
        self.key = key if key else self.KEY
        self.supabase_client = create_client(self.server_url, self.KEY)
        
    def insert(self, table_name, data):
        res = self.supabase_client.table(table_name).insert(data).execute()
        
        # add error handling
        return res
    
    def fetch(self, vector):
        """ use SQL to perfrom fetching"""
        pass

    def fetch_base64_by_ids(self, table_name, ids):
        # there are more than one moment with the same id
        # just fetch the first appearing moment for each id
        frames = []
        for id in ids:
            response = self.supabase_client.table(table_name).select("*").eq("moment_id", id).limit(1).execute()
            data = response.data[0]
            frame_base64 = data.get('frame_base64')
            frames.append(frame_base64)

            # type of response is APIResponse
            # data of response APIResponse is as follows: 'data=[{'id': 1, 'created_at': ..., 'frame_base64': ..., 'moment_id': 1, 'vector': ...}]'
        
        return frames