from database import supabase
from typing import Optional, List, Dict

class SongDAO:
    TABLE = "songs"

    def create_song(self, title: str, duration: Optional[int] = None) -> Optional[Dict]:
        song_data = {
            "title": title,
        }
        if duration is not None:
            song_data["duration"] = duration
        response = supabase.table(self.TABLE).insert(song_data).execute()
        if response.data:
            return response.data[0]
        else:
            print("Failed to create song.")
            return None

    def get_song_by_id(self, song_id: str) -> Optional[Dict]:
        response = supabase.table(self.TABLE).select("*").eq("song_id", song_id).execute()
        if response.data:
            return response.data[0]
        else:
            print("Song not found.")
            return None

    def update_song(self, song_id: str, title: Optional[str] = None, duration: Optional[int] = None) -> bool:
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if duration is not None:
            update_data["duration"] = duration

        if not update_data:
            print("No fields to update.")
            return False

        response = supabase.table(self.TABLE).update(update_data).eq("song_id", song_id).execute()
        if response.data:
            return True
        else:
            print("Failed to update song.")
            return False

    def delete_song(self, song_id: str) -> bool:
        response = supabase.table(self.TABLE).delete().eq("song_id", song_id).execute()
        if response.data:
            return True
        else:
            print("Failed to delete song.")
            return False

    def list_songs(self) -> List[Dict]:
        response = supabase.table(self.TABLE).select("*").execute()
        if response.data:
            return response.data
        else:
            return []
