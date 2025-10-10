from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class ReportDAO:
    def count_users_by_role(self):
        res = supabase.rpc("count_users_by_role").execute()
        return res.data if res and res.data else []

    def count_playlists_by_mood(self):
        res = supabase.rpc("count_playlists_by_mood").execute()
        return res.data if res and res.data else []
