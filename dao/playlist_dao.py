from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class PlaylistDAO:
    def create_playlist(self, data):
        return supabase.table("playlists").insert(data).execute()

    def get_playlists_by_user(self, user_id):
        res = supabase.table("playlists").select("*").eq("user_id", user_id).execute()
        return res.data if res and res.data else []

    def update_playlist(self, playlist_id, update_data, user_id):
        return supabase.table("playlists").update(update_data).eq("id", playlist_id).eq("user_id", user_id).execute()

    def delete_playlist(self, playlist_id):
        return supabase.table("playlists").delete().eq("id", playlist_id).execute()

    def get_songs_in_playlist(self, playlist_id):
        res = supabase.table("playlist_songs") \
            .select("song_id, songs(title)") \
            .eq("playlist_id", playlist_id) \
            .execute()
        return res.data if res.data else []

    def add_song_to_playlist(self, playlist_id, song_id):
        return supabase.table("playlist_songs").insert({
            "playlist_id": playlist_id,
            "song_id": song_id
        }).execute()

    def remove_song_from_playlist(self, playlist_id, song_id):
        return supabase.table("playlist_songs").delete().eq("playlist_id", playlist_id).eq("song_id", song_id).execute()

    def list_playlists_by_mood(self, mood_id):
        res = supabase.table("playlists").select("*").eq("mood_id", mood_id).execute()
        return res.data if res.data else []
    def get_playlists_by_mood(self, mood_id):
        """Fetch playlists associated with a given mood."""
        try:
            res = supabase.table("playlists").select("*").eq("mood_id", mood_id).execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"❌ Error fetching playlists by mood: {e}")
            return []

