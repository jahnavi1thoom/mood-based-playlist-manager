from database import supabase
from typing import Optional, List, Dict

class ArtistDAO:
    TABLE = "artists"

    def create_artist(self, name: str, description: Optional[str] = None) -> Optional[Dict]:
        artist_data = {
            "name": name,
            "description": description
        }
        # Remove None values
        artist_data = {k: v for k, v in artist_data.items() if v is not None}
        response = supabase.table(self.TABLE).insert(artist_data).execute()
        if response.data:
            return response.data[0]
        else:
            print("Failed to create artist.")
            return None

    def get_artist_by_id(self, artist_id: str) -> Optional[Dict]:
        response = supabase.table(self.TABLE).select("*").eq("artist_id", artist_id).execute()
        if response.data:
            return response.data[0]
        else:
            print("Artist not found.")
            return None

    def update_artist(self, artist_id: str, name: Optional[str] = None, description: Optional[str] = None) -> bool:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        if not update_data:
            print("No fields to update.")
            return False

        response = supabase.table(self.TABLE).update(update_data).eq("artist_id", artist_id).execute()
        if response.data:
            return True
        else:
            print("Failed to update artist.")
            return False

    def delete_artist(self, artist_id: str) -> bool:
        response = supabase.table(self.TABLE).delete().eq("artist_id", artist_id).execute()
        if response.data:
            return True
        else:
            print("Failed to delete artist.")
            return False

    def list_artists(self) -> List[Dict]:
        response = supabase.table(self.TABLE).select("*").execute()
        if response.data:
            return response.data
        else:
            return []
