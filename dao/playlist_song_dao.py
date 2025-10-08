from database import supabase
from typing import List, Optional, Dict

class PlaylistSongDAO:
    TABLE = "playlist_songs"

    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> bool:
        record = {
            "playlist_id": playlist_id,
            "song_id": song_id
        }
        response = supabase.table(self.TABLE).insert(record).execute()
        return bool(response.data)

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> bool:
        response = supabase.table(self.TABLE).delete() \
            .eq("playlist_id", playlist_id).eq("song_id", song_id).execute()
        return bool(response.data)

    def list_songs_in_playlist(self, playlist_id: str) -> List[Dict]:
        response = supabase.table(self.TABLE).select("song_id").eq("playlist_id", playlist_id).execute()
        if response.data:
            return response.data
        return []

    def list_playlists_containing_song(self, song_id: str) -> List[Dict]:
        response = supabase.table(self.TABLE).select("playlist_id").eq("song_id", song_id).execute()
        if response.data:
            return response.data
        return []
