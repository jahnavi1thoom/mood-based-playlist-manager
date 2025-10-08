from database import supabase
from typing import Optional, List, Dict
import datetime

class PlaylistDAO:
    TABLE = "playlists"

    def create_playlist(self, user_id: str, name: str, description: str = "", mood_id: Optional[str] = None) -> Optional[Dict]:
        playlist_data = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "mood_id": mood_id
        }
        response = supabase.table(self.TABLE).insert(playlist_data).execute()
        if response.data:
            return response.data[0]
        else:
            print("Error creating playlist:", getattr(response, 'error', 'Unknown error'))
            return None

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Dict]:
        response = supabase.table(self.TABLE).select("*").eq("playlist_id", playlist_id).execute()
        if response.data:
            return response.data[0]
        else:
            print("Playlist not found.")
            return None

    def update_playlist(self, playlist_id: str, name: Optional[str] = None,
                        description: Optional[str] = None, mood_id: Optional[str] = None) -> bool:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if mood_id is not None:
            update_data["mood_id"] = mood_id

        if not update_data:
            print("No update fields provided.")
            return False

        response = supabase.table(self.TABLE).update(update_data).eq("playlist_id", playlist_id).execute()
        if response.data:
            return True
        else:
            print("Failed to update playlist.")
            return False

    def delete_playlist(self, playlist_id: str) -> bool:
        response = supabase.table(self.TABLE).delete().eq("playlist_id", playlist_id).execute()
        if response.data:
            return True
        else:
            print("Failed to delete playlist.")
            return False

    def list_playlists(self) -> List[Dict]:
        response = supabase.table(self.TABLE).select("*").execute()
        if response.data:
            return response.data
        else:
            return []
    def list_playlists_by_mood(self, mood_id: Optional[str]) -> List[Dict]:
        if mood_id is None:
            return []  # no mood selected means no playlists

        response = supabase.table(self.TABLE).select("*").eq("mood_id", mood_id).execute()
        if response.data:
            return response.data
        else:
            print(f"No playlists found for mood_id: {mood_id}")
            return []
