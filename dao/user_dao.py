from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class UserDAO:
    def create_user(self, username, email, password_hash, role="User"):
        return supabase.table("users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role
        }).execute()

    def list_all_users(self):
        res = supabase.table("users").select("*").execute()
        return res.data if res and res.data else []

    def update_user(self, user_id, username, email, role):
        return supabase.table("users").update({
            "username": username,
            "email": email,
            "role": role
        }).eq("user_id", user_id).execute()

    def delete_user(self, user_id):
        return supabase.table("users").delete().eq("user_id", user_id).execute()
