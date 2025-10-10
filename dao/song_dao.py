from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class SongDAO:
    def create_song(self, title, duration):
        return supabase.table("songs").insert({
            "title": title,
            "duration": duration,
            "created_at": datetime.now().isoformat()
        }).execute()

    def list_songs(self):
        res = supabase.table("songs").select("*").execute()
        return res.data if res and res.data else []

    def list_songs_for_user(self, user_id):
        res = supabase.table("songs").select("*").execute()
        return res.data if res and res.data else []

    def update_song(self, song_id, title=None, duration=None):
        data = {}
        if title: data["title"] = title
        if duration: data["duration"] = duration
        return supabase.table("songs").update(data).eq("song_id", song_id).execute()

    def delete_song(self, song_id):
        return supabase.table("songs").delete().eq("song_id", song_id).execute()
