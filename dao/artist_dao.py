from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class ArtistDAO:
    def create_artist(self, user_id, name, description=None):
        return supabase.table("artists").insert({
            "user_id": user_id,
            "name": name,
            "description": description or "",
            "created_at": datetime.now().isoformat()
        }).execute()

    def get_artists_by_user(self, user_id):
        res = supabase.table("artists").select("*").eq("user_id", user_id).execute()
        return res.data if res.data else []

    def update_artist(self, artist_id, user_id, name=None, description=None):
        data = {}
        if name: data["name"] = name
        if description: data["description"] = description
        return supabase.table("artists").update(data).eq("artist_id", artist_id).eq("user_id", user_id).execute()

    def delete_artist(self, artist_id, user_id):
        return supabase.table("artists").delete().eq("artist_id", artist_id).eq("user_id", user_id).execute()
