import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

from dao.user_dao import UserDAO
from dao.playlist_dao import PlaylistDAO
from dao.mood_dao import MoodDAO
from dao.playlist_song_dao import PlaylistSongDAO
from dao.song_dao import SongDAO
from dao.artist_dao import ArtistDAO
from dao.report_dao import ReportDAO

def playlist_songs_ui(playlist_id):
    song_dao = SongDAO()
    playlist_song_dao = PlaylistSongDAO()

    all_songs = song_dao.list_songs()
    song_id_map = {song['title']: song['song_id'] for song in all_songs}
    current_links = playlist_song_dao.list_songs_in_playlist(playlist_id)
    current_song_ids = {link['song_id'] for link in current_links}

    st.subheader("Songs in Playlist")
    for song in all_songs:
        if song['song_id'] in current_song_ids:
            cols = st.columns([8, 2])
            cols[0].write(song['title'])
            if cols[1].button(f"Remove {song['title']}", key=f"remove_{song['song_id']}"):
                playlist_song_dao.remove_song_from_playlist(playlist_id, song['song_id'])
                st.rerun()

    st.markdown("---")
    remaining_songs = [s['title'] for s in all_songs if s['song_id'] not in current_song_ids]
    if remaining_songs:
        selection = st.selectbox("Add Song to Playlist", remaining_songs)
        if st.button("Add Song"):
            playlist_song_dao.add_song_to_playlist(playlist_id, song_id_map[selection])
            st.rerun()
    else:
        st.info("All songs already in this playlist.")

# ---------- Authentication helpers ----------

def ensure_auth_state():
    if "auth" not in st.session_state:
        st.session_state.auth = {"user": None, "email": None, "access_token": None, "role": None}

def ensure_profile(user_id: str, email: str):
    try:
        resp = supabase.table("users").select("user_id").eq("auth_user_id", user_id).maybe_single().execute()
        data = getattr(resp, "data", None)
        if not data:
            username = (email or "").split("@")[0] or "user"
            ins = {
                "auth_user_id": user_id,
                "username": username,
                "email": email,
                "role": "User"
            }
            supabase.table("users").insert(ins).execute()
    except Exception as e:
        st.error(f"Profile sync skipped: {e}")

def fetch_role_by_auth(user_id: str) -> str:
    try:
        resp = supabase.table("users").select("role").eq("auth_user_id", user_id).limit(1).execute()
        rows = getattr(resp, "data", []) or []
        return rows[0].get("role", "User") if rows else "User"
    except:
        return "User"

def sign_in(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user and res.session:
            ensure_profile(res.user.id, email)
            st.session_state.auth["user"] = {"id": res.user.id}
            st.session_state.auth["email"] = email
            st.session_state.auth["access_token"] = res.session.access_token
            st.session_state.auth["role"] = fetch_role_by_auth(res.user.id)
            st.rerun()
        else:
            st.error("Invalid credentials or error during sign in.")
    except Exception as e:
        st.error(f"Sign in failed: {e}")

def sign_up(email: str, password: str):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            ensure_profile(res.user.id, email)
        st.success("Account created. If email confirmation is enabled, check your inbox then log in.")
    except Exception as e:
        st.error(f"Sign up failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.auth = {"user": None, "email": None, "access_token": None, "role": None}
    st.rerun()

def login_screen():
    st.title("Mood-Based Playlist Manager")
    st.subheader("Login or Register to continue")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                sign_in(email, password)

    with tab2:
        with st.form("register_form"):
            email_r = st.text_input("Email", key="reg_email")
            password_r = st.text_input("Password", type="password", key="reg_pass")
            if st.form_submit_button("Register"):
                sign_up(email_r, password_r)

def topbar():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption(f"Signed in as: {st.session_state.auth.get('email', 'Unknown')} | Role: {st.session_state.auth.get('role', 'User')}")
    with col2:
        if st.button("Sign out"):
            sign_out()
def button_bar(options):
    cols = st.columns(len(options))
    for idx, option in enumerate(options):
        if cols[idx].button(option.capitalize()):
            st.session_state.active_module = option
    return st.session_state.get("active_module")
# ---------- Mood-based Playlists feature ----------

def mood_playlist_view():
    mood_dao = MoodDAO()
    playlist_dao = PlaylistDAO()
    
    moods = mood_dao.list_moods()
    if not moods:
        st.info("No moods found.")
        return
    
    mood_options = {m.get('mood_name', 'Unknown Mood'): m.get('mood_id') for m in moods}
    selected_mood_name = st.selectbox("Select Mood", list(mood_options.keys()))
    if selected_mood_name:
        selected_mood_id = mood_options.get(selected_mood_name)
        playlists = playlist_dao.list_playlists_by_mood(selected_mood_id)
        if not playlists:
            st.info(f"No playlists found for mood '{selected_mood_name}'.")
            return
        
        st.subheader(f"Playlists for Mood: {selected_mood_name}")
        for playlist in playlists:
            st.write(f"**{playlist.get('name', '<Unnamed>')}**")
            desc = playlist.get('description', '')
            if desc:
                st.write(f"Description: {desc}")
            st.write("---")
    
   

def display_crud_table(entity_name, dao, list_method_name):
    st.subheader(f"{entity_name.capitalize()} Management")

    if entity_name == "reports":
        st.subheader("Reports")
        report_type = st.selectbox("Select Report", ["Users by Role", "Playlists by Mood"])
        if report_type == "Users by Role":
            data = dao.count_users_by_role()
            st.table(data or [])
        else:
            data = dao.count_playlists_by_mood()
            st.table(data or [])
        return

    try:
        list_method = getattr(dao, list_method_name)
        records = list_method()
    except Exception as e:
        st.error(f"Error loading {entity_name}: {e}")
        return

    if not records:
        st.info(f"No {entity_name} records found.")
        records = []

    df = pd.DataFrame(records)
    search_term = st.text_input(f"Search {entity_name}s", key=f"search_{entity_name}")
    filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)] if search_term else df
    st.dataframe(filtered_df, use_container_width=True)

    # Users CRUD (Admin only)
    if entity_name == "users":
        if st.session_state.auth.get("role") != "Admin":
            st.warning("Access restricted to Admin.")
            return

        with st.expander("Create New User"):
            with st.form(f"create_{entity_name}_form", clear_on_submit=True):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["Admin", "User"])
                if st.form_submit_button("Create"):
                    try:
                        dao.create_user(username, email, password, role)
                        st.success("User created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating user: {e}")

        records_dicts = filtered_df.to_dict("records") if not filtered_df.empty else []
        ids = [r.get("user_id") for r in records_dicts if r.get("user_id") is not None]
        if not ids:
            st.info(f"No {entity_name} records available.")
            return
        selected_id = st.selectbox(f"Select {entity_name[:-1].capitalize()} to View/Update/Delete", ids, key=f"select_{entity_name}")
        action = st.radio("Select Action", ["View", "Update", "Delete"], horizontal=True, key=f"action_{entity_name}")
        selected_record = next((r for r in records if r.get('user_id') == selected_id), None)
        if selected_record:
            if action == "View":
                st.json(selected_record)
            elif action == "Update":
                with st.form(f"update_{entity_name}_form"):
                    username = st.text_input("Username", selected_record.get("username", ""))
                    email = st.text_input("Email", selected_record.get("email", ""))
                    role_list = ["Admin", "User"]
                    role_value = selected_record.get("role", "User")
                    default_index = next((i for i, v in enumerate(role_list) if v.lower() == (role_value or "").lower()), 1)
                    role = st.selectbox("Role", role_list, index=default_index)
                    if st.form_submit_button("Update"):
                        try:
                            dao.update_user(selected_id, username, email, role)
                            st.success(f"{entity_name[:-1].capitalize()} updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating user: {e}")
            else:
                if st.button(f"Confirm Delete {entity_name[:-1].capitalize()}", key=f"delete_{entity_name}"):
                    try:
                        dao.delete_user(selected_id)
                        st.success(f"{entity_name[:-1].capitalize()} deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting user: {e}")

    # Playlists CRUD
    elif entity_name == "playlists":
        dao_user = UserDAO()
        users = dao_user.list_all_users()
        user_options = [(u['username'], u['user_id']) for u in users]
        with st.expander("Create New Playlist"):
            with st.form(f"create_{entity_name}_form", clear_on_submit=True):
                selected_user = st.selectbox("Select User", user_options, format_func=lambda x: x[0])
                user_id = selected_user[1] if selected_user else None
                name = st.text_input("Playlist Name")
                description = st.text_area("Description")
                mood_id = st.text_input("Mood ID (optional)")
                if st.form_submit_button("Create"):
                    try:
                        dao.create_playlist(user_id, name, description, mood_id if mood_id else None)
                        st.success("Playlist created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating playlist: {e}")

        records_dicts = filtered_df.to_dict("records") if not filtered_df.empty else []
        ids = [r.get('playlist_id') for r in records_dicts if r.get('playlist_id') is not None]
        if not ids:
            st.info(f"No {entity_name} records available.")
            return
        selected_id = st.selectbox("Select Playlist to View/Update/Delete", ids, key=f"select_{entity_name}")
        action = st.radio("Select Action", ["View", "Update", "Delete"], horizontal=True, key=f"action_{entity_name}")
        selected_record = next((r for r in records if r.get('playlist_id') == selected_id), None)
        if selected_record:
            if action == "View":
                st.json(selected_record)
            elif action == "Update":
                with st.form(f"update_{entity_name}_form"):
                    name = st.text_input("Name", selected_record.get("name", ""))
                    description = st.text_area("Description", selected_record.get("description", ""))
                    moods = MoodDAO().list_moods()
                    mood_options = {m["mood_name"]: m["mood_id"] for m in moods}
                    mood_name_by_id = {v: k for k, v in mood_options.items()}
                    current_mood = mood_name_by_id.get(selected_record.get("mood_id"), "")
                    selected_mood = st.selectbox("Mood", [""] + list(mood_options.keys()), index=(list(mood_options.keys()) + [""]).index(current_mood))
                    selected_mood_id = mood_options.get(selected_mood) if selected_mood else None
                    if st.form_submit_button("Update"):
                        try:
                            dao.update_playlist(selected_record["playlist_id"], name=name, description=description, mood_id=selected_mood_id)
                            st.success("Playlist updated")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                # Add playlist song management here, below update form
                playlist_songs_ui(selected_record["playlist_id"])

            else:
                if st.button("Confirm Delete Playlist", key=f"delete_{entity_name}"):
                    try:
                        dao.delete_playlist(selected_id)
                        st.success("Playlist deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting playlist: {e}")
            

    # Moods CRUD
    elif entity_name == "moods":
        with st.expander("Create New Mood"):
            with st.form(f"create_{entity_name}_form", clear_on_submit=True):
                mood_name = st.text_input("Mood Name")
                description = st.text_area("Description")
                if st.form_submit_button("Create"):
                    try:
                        dao.create_mood(mood_name, description)
                        st.success("Mood created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating mood: {e}")

        records_dicts = filtered_df.to_dict("records") if not filtered_df.empty else []
        ids = [r.get('mood_id') for r in records_dicts if r.get('mood_id') is not None]
        if not ids:
            st.info(f"No {entity_name} records available.")
            return
        selected_id = st.selectbox("Select Mood to View/Update/Delete", ids, key=f"select_{entity_name}")
        action = st.radio("Select Action", ["View", "Update", "Delete"], horizontal=True, key=f"action_{entity_name}")
        selected_record = next((r for r in records if r.get('mood_id') == selected_id), None)
        if selected_record:
            if action == "View":
                st.json(selected_record)
            elif action == "Update":
                with st.form(f"update_{entity_name}_form"):
                    mood_name = st.text_input("Mood Name", selected_record.get("mood_name", ""))
                    description = st.text_area("Description", selected_record.get("description", ""))
                    if st.form_submit_button("Update"):
                        try:
                            dao.update_mood(selected_id, mood_name=mood_name, description=description)
                            st.success("Mood updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating mood: {e}")
            else:
                if st.button(f"Confirm Delete Mood", key=f"delete_{entity_name}"):
                    try:
                        dao.delete_mood(selected_id)
                        st.success("Mood deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting mood: {e}")

    # Songs CRUD
    elif entity_name == "songs":
        with st.expander("Create New Song"):
            with st.form(f"create_{entity_name}_form", clear_on_submit=True):
                title = st.text_input("Title")
                duration = st.number_input("Duration (seconds)", min_value=0, step=1)
                if st.form_submit_button("Create"):
                    try:
                        dao.create_song(title, duration)
                        st.success("Song created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating song: {e}")

        records_dicts = filtered_df.to_dict("records") if not filtered_df.empty else []
        ids = [r.get('song_id') for r in records_dicts if r.get('song_id') is not None]
        if not ids:
            st.info(f"No {entity_name} records available.")
            return
        selected_id = st.selectbox("Select Song to View/Update/Delete", ids, key=f"select_{entity_name}")
        action = st.radio("Select Action", ["View", "Update", "Delete"], horizontal=True, key=f"action_{entity_name}")
        selected_record = next((r for r in records if r.get('song_id') == selected_id), None)
        if selected_record:
            if action == "View":
                st.json(selected_record)
            elif action == "Update":
                with st.form(f"update_{entity_name}_form"):
                    title = st.text_input("Title", selected_record.get("title", ""))
                    duration = st.number_input("Duration (seconds)", min_value=0, step=1, value=selected_record.get("duration") or 0)
                    if st.form_submit_button("Update"):
                        try:
                            dao.update_song(selected_id, title=title, duration=duration)
                            st.success("Song updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating song: {e}")
            else:
                if st.button(f"Confirm Delete Song", key=f"delete_{entity_name}"):
                    try:
                        dao.delete_song(selected_id)
                        st.success("Song deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting song: {e}")

    # Artists CRUD
    elif entity_name == "artists":
        with st.expander("Create New Artist"):
            with st.form(f"create_{entity_name}_form", clear_on_submit=True):
                name = st.text_input("Artist Name")
                description = st.text_area("Description")
                if st.form_submit_button("Create"):
                    try:
                        dao.create_artist(name, description if description else None)
                        st.success("Artist created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating artist: {e}")

        records_dicts = filtered_df.to_dict("records") if not filtered_df.empty else []
        ids = [r.get('artist_id') for r in records_dicts if r.get('artist_id') is not None]
        if not ids:
            st.info(f"No {entity_name} records available.")
            return
        selected_id = st.selectbox("Select Artist to View/Update/Delete", ids, key=f"select_{entity_name}")
        action = st.radio("Select Action", ["View", "Update", "Delete"], horizontal=True, key=f"action_{entity_name}")
        selected_record = next((r for r in records if r.get('artist_id') == selected_id), None)
        if selected_record:
            if action == "View":
                st.json(selected_record)
            elif action == "Update":
                with st.form(f"update_{entity_name}_form"):
                    name = st.text_input("Artist Name", selected_record.get("name", ""))
                    description = st.text_area("Description", selected_record.get("description", ""))
                    if st.form_submit_button("Update"):
                        try:
                            dao.update_artist(selected_id, name=name, description=description)
                            st.success("Artist updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating artist: {e}")
            else:
                if st.button(f"Confirm Delete Artist", key=f"delete_{entity_name}"):
                    try:
                        dao.delete_artist(selected_id)
                        st.success("Artist deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting artist: {e}")

# New playlists_by_mood UI module
def mood_playlist_view():
    mood_dao = MoodDAO()
    playlist_dao = PlaylistDAO()
    
    moods = mood_dao.list_moods()
    if not moods:
        st.info("No moods found.")
        return
    
    mood_options = {m.get('mood_name', 'Unknown Mood'): m.get('mood_id') for m in moods}
    selected_mood_name = st.selectbox("Select Mood", list(mood_options.keys()))
    if selected_mood_name:
        selected_mood_id = mood_options.get(selected_mood_name)
        playlists = playlist_dao.list_playlists_by_mood(selected_mood_id)
        if not playlists:
            st.info(f"No playlists found for mood '{selected_mood_name}'.")
            return
        
        st.subheader(f"Playlists for Mood: {selected_mood_name}")
        for playlist in playlists:
            st.write(f"**{playlist.get('name', '<Unnamed>')}**")
            desc = playlist.get('description', '')
            if desc:
                st.write(f"Description: {desc}")
            st.write("---")

def main():
    # Ensure auth state
    if "auth" not in st.session_state:
        st.session_state.auth = {"user": None, "email": None, "access_token": None, "role": None}
    
    # Authentication UI
    if not st.session_state.auth.get("user"):
        login_screen()
        return

    topbar()
    st.title("Mood-Based Playlist Manager")
    if "active_module" not in st.session_state:
        st.session_state.active_module = "playlists"

    # Map to manage all modules
    dao_map = {
        "users": (UserDAO(), "list_all_users"),
        "playlists": (PlaylistDAO(), "list_playlists"),
        "moods": (MoodDAO(), "list_moods"),
        "songs": (SongDAO(), "list_songs"),
        "artists": (ArtistDAO(), "list_artists"),
        "reports": (ReportDAO(), "count_users_by_role"),
        "playlists_by_mood": (None, None)
    }

    modules = list(dao_map.keys())
    current_module = button_bar(modules)

    # Mood filtered playlists
    if current_module == "playlists_by_mood":
        mood_playlist_view()
    elif current_module:
        dao, method = dao_map[current_module]
        display_crud_table(current_module, dao, method)
    else:
        st.info("Select a module above to manage data.")


if __name__ == "__main__":
    main()