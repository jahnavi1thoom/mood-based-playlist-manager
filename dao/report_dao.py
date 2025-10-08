from typing import Optional, List, Dict
from database import supabase

class ReportDAO:
    def count_users_by_role(self) -> Optional[List[Dict]]:
        response = supabase.table("users").select("role").execute()
        if response.data:
            counts = {}
            for user in response.data:
                role = user.get("role", "Unknown")
                counts[role] = counts.get(role, 0) + 1
            return [{"role": role, "count": count} for role, count in counts.items()]
        else:
            print("No data found.")
            return None

    def count_playlists_by_mood(self) -> Optional[List[Dict]]:
        response = supabase.table("playlists").select("mood_id").execute()
        if response.data:
            counts = {}
            for pl in response.data:
                mood_id = pl.get("mood_id", "Unknown")
                counts[mood_id] = counts.get(mood_id, 0) + 1
            return [{"mood_id": mood_id, "count": count} for mood_id, count in counts.items()]
        else:
            print("No data found.")
            return None
