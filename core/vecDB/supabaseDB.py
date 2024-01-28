from supabase import create_client, Client

class SupabaseDB:
    SERVER_URL = "https://augwkisabfpevnwvzzqu.supabase.co"
    KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1Z3draXNhYmZwZXZud3Z6enF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDQxODEyNjQsImV4cCI6MjAxOTc1NzI2NH0.fCq73M9nXjKriNMNOYnFsxzH8_cdUpiNlyh9_XioREI"
    supabase_client: Client
    
    def __init__(self) -> None:
        self.supabase_client = create_client(self.SERVER_URL, self.KEY)
        
    def insert(self, table_name, data):
        res = self.supabase_client.table(table_name).insert(data).execute()
        
        # add error handling
        return res
    
    def fetch(self, vector):
        pass