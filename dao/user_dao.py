from database import supabase
from typing import Optional, List, Dict
import datetime

class UserDAO:
    TABLE = "users"

    def create_user(self, username: str, email: str, password_hash: str, role: str = "User") -> Optional[dict]:
        existing_user = self.get_user_by_email(email)
        if existing_user:
            print(f"Error: A user with email '{email}' already exists.")
            return None

        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        response = supabase.table(self.TABLE).insert(user_data).execute()

        if response.data:
            return response.data[0]
        else:
            print("Error creating user:", getattr(response, 'error', 'Unknown error'))
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        response = supabase.table(self.TABLE).select("*").eq("email", email).execute()
        if response.data:
            return response.data[0]
        return None

    def update_user(self, user_id: str, username: str, email: str, role: str) -> bool:
        update_data = {
            "username": username,
            "email": email,
            "role": role
            # Remove updated_at if not in your DB schema
        }
        response = supabase.table(self.TABLE).update(update_data).eq("user_id", user_id).execute()
        if response.data:
            return True
        else:
            print("Failed to update user.")
            return False


    def delete_user(self, user_id: str) -> bool:
        response = supabase.table(self.TABLE).delete().eq("user_id", user_id).execute()
        if response.data:
            return True
        else:
            print("Failed to delete user.")
            return False

    def list_all_users(self) -> List[Dict]:
        response = supabase.table(self.TABLE).select("*").execute()
        return response.data if response.data else []
