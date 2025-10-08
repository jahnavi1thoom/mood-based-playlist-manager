from database import supabase
from typing import Optional, List, Dict
import datetime

class MoodDAO:
    TABLE = "moods"

    def create_mood(self, mood_name: str, description: str = "") -> Optional[Dict]:
        mood_data = {
            "mood_name": mood_name,
            "description": description,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        response = supabase.table(self.TABLE).insert(mood_data).execute()
        if response.data:
            return response.data[0]
        else:
            print("Error creating mood:", getattr(response, 'error', 'Unknown error'))
            return None

    def get_mood_by_id(self, mood_id: str) -> Optional[Dict]:
        response = supabase.table(self.TABLE).select("*").eq("mood_id", mood_id).execute()
        if response.data:
            return response.data[0]
        else:
            print("Mood not found.")
            return None

    def update_mood(self, mood_id: str, mood_name: Optional[str] = None, description: Optional[str] = None) -> bool:
        update_data = {}
        if mood_name is not None:
            update_data["mood_name"] = mood_name
        if description is not None:
            update_data["description"] = description

        if not update_data:
            print("No update fields provided.")
            return False

        response = supabase.table(self.TABLE).update(update_data).eq("mood_id", mood_id).execute()
        if response.data:
            return True
        else:
            print("Failed to update mood.")
            return False

    def delete_mood(self, mood_id: str) -> bool:
        response = supabase.table(self.TABLE).delete().eq("mood_id", mood_id).execute()
        if response.data:
            return True
        else:
            print("Failed to delete mood.")
            return False

    def list_moods(self) -> List[Dict]:
        response = supabase.table(self.TABLE).select("*").execute()
        if response.data:
            return response.data
        else:
            return []
