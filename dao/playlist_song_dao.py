from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class PlaylistSongDAO:
    def add_song_to_playlist(self, playlist_id, song_id):
        return supabase.table("playlist_songs").insert({
            "playlist_id": playlist_id,
            "song_id": song_id
        }).execute()

    def remove_song_from_playlist(self, playlist_id, song_id):
        return supabase.table("playlist_songs").delete().eq("playlist_id", playlist_id).eq("song_id", song_id).execute()

    def list_songs_in_playlist(self, playlist_id):
        res = supabase.rpc("get_songs_in_playlist", {"playlist_uuid": playlist_id}).execute()
        return res.data if res and res.data else []
