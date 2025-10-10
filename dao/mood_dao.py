from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class MoodDAO:
    def create_mood(self, user_id, mood_name, description=""):
        """Insert a new mood for a specific user."""
        try:
            res = supabase.table("moods").insert({
                "user_id": user_id,
                "mood_name": mood_name,
                "description": description,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"❌ Error creating mood: {e}")
            return None

    def list_moods(self):
        """Fetch all moods."""
        try:
            res = supabase.table("moods").select("mood_id, mood_name, description, created_at").execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"❌ Error listing moods: {e}")
            return []

    def get_moods_by_user(self, user_id):
        """Fetch moods for a given user."""
        try:
            res = supabase.table("moods").select("mood_id, mood_name, description, created_at").eq("user_id", user_id).execute()
            return res.data if res.data else []
        except Exception as e:
            print("⚠️ get_moods_by_user() fallback (no user_id):", e)
            # fallback: return all moods if filtering fails
            try:
                res = supabase.table("moods").select("mood_id, mood_name, description, created_at").execute()
                return res.data if res.data else []
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                return []

    def update_mood(self, mood_id, user_id, mood_name=None, description=None):
        """Update mood name or description."""
        data = {}
        if mood_name:
            data["mood_name"] = mood_name
        if description:
            data["description"] = description
        try:
            res = supabase.table("moods").update(data).eq("mood_id", mood_id).eq("user_id", user_id).execute()
            return res.data if res.data else None
        except Exception as e:
            print(f"❌ Error updating mood: {e}")
            return None

    def delete_mood(self, mood_id, user_id):
        """Delete a mood by mood_id."""
        try:
            res = supabase.table("moods").delete().eq("mood_id", mood_id).eq("user_id", user_id).execute()
            return res.data if res.data else None
        except Exception as e:
            print(f"❌ Error deleting mood: {e}")
            return None
