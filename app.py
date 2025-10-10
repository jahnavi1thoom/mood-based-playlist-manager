# app.py — Complete robust Streamlit app for Mood-Based Playlist Manager
import streamlit as st
import pandas as pd
from datetime import datetime,timezone
import hashlib
from dotenv import load_dotenv
import os
from supabase import create_client
import uuid

# -------------------------
# Load env & create supabase
# -------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Import DAO classes (must exist in dao/ folder)
# -------------------------
from dao.user_dao import UserDAO
from dao.playlist_dao import PlaylistDAO
from dao.mood_dao import MoodDAO
from dao.song_dao import SongDAO
from dao.artist_dao import ArtistDAO
from dao.playlist_song_dao import PlaylistSongDAO
from dao.report_dao import ReportDAO

# -------------------------
# Small helpers
# -------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _data_of(resp):
    """Normalize supabase/DAO response to python data (list/dict)"""
    if resp is None:
        return None
    if hasattr(resp, "data"):
        return resp.data
    return resp

# -------------------------
# Flexible DAO wrappers
# These try multiple common method names/signatures so app works with slightly different DAOs
# -------------------------
def list_playlists_for_user(dao: PlaylistDAO, user_id: str):
    candidates = [
        ("list_playlists_by_user", (user_id,)),
        ("get_playlists_by_user", (user_id,)),
        ("list_playlists", (user_id,)),
        ("list_playlists", ()),
        ("get_playlists", (user_id,)),
        ("get_playlists", ()),
    ]
    for name, args in candidates:
        if hasattr(dao, name):
            try:
                res = getattr(dao, name)(*args)
                data = _data_of(res)
                if data is not None:
                    return data if isinstance(data, list) else [data]
            except TypeError:
                # try without args
                try:
                    res = getattr(dao, name)()
                    data = _data_of(res)
                    if data is not None:
                        return data if isinstance(data, list) else [data]
                except Exception:
                    pass
            except Exception:
                pass
    # fallback to direct supabase query
    try:
        r = supabase.table("playlists").select("*").eq("user_id", user_id).execute()
        return r.data or []
    except Exception:
        return []

def create_playlist_flexible(dao: PlaylistDAO, user_id: str, name: str, description: str = "", mood_id: str = None):
    candidates = [
        ("create_playlist", (user_id, name, description, mood_id)),
        ("create_playlist", (name, description, mood_id, user_id)),
        ("create_playlist", (name, description, mood_id)),
        ("create_playlist", ({"playlist_id": str(uuid.uuid4()), "user_id": user_id, "playlist_name": name, "description": description, "mood_id": mood_id, "created_at": datetime.now(timezone.utc).isoformat()},)),
    ]
    for nm, args in candidates:
        if hasattr(dao, nm):
            try:
                res = getattr(dao, nm)(*args)
                data = _data_of(res)
                if data:
                    return data[0] if isinstance(data, list) else data
            except Exception:
                pass
    # final fallback: insert directly
    try:
        payload = {
            "playlist_id": str(uuid.uuid4()),
            "playlist_name": name,
            "user_id": user_id,
            "mood_id": mood_id,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat()  # ✅ fixed
        }
        r = supabase.table("playlists").insert(payload).execute()
        return r.data[0] if getattr(r, "data", None) else None
    except Exception as e:
        print("Error creating playlist:", e)
        return None

def update_playlist_flexible(dao: PlaylistDAO, playlist_id: str, user_id: str = None, name: str = None, description: str = None, mood_id: str = None):
    candidates = [
        ("update_playlist", (playlist_id, name, description, mood_id)),
        ("update_playlist", (playlist_id, {"playlist_name": name, "description": description, "mood_id": mood_id})),
        ("update_playlist", (playlist_id, name)),
        ("update_playlist", (playlist_id, {"playlist_name": name})),
    ]
    for nm, args in candidates:
        if hasattr(dao, nm):
            try:
                res = getattr(dao, nm)(*args)
                return True
            except Exception:
                pass
    # fallback to supabase update
    try:
        upd = {}
        if name is not None: upd["playlist_name"] = name
        if description is not None: upd["description"] = description
        if mood_id is not None: upd["mood_id"] = mood_id
        if not upd:
            return False
        r = supabase.table("playlists").update(upd).eq("playlist_id", playlist_id).execute()
        return bool(getattr(r, "data", None))
    except Exception:
        return False

def delete_playlist_flexible(dao: PlaylistDAO, playlist_id: str, user_id: str = None):
    candidates = [
        ("delete_playlist", (playlist_id,)),
        ("delete_playlist", (playlist_id, user_id)),
        ("delete_playlist_by_id", (playlist_id,)),
    ]
    for nm, args in candidates:
        if hasattr(dao, nm):
            try:
                res = getattr(dao, nm)(*args)
                return True
            except Exception:
                pass
    try:
        r = supabase.table("playlists").delete().eq("playlist_id", playlist_id).execute()
        return bool(getattr(r, "data", None))
    except Exception:
        return False

def add_song_to_playlist_flexible(playlist_dao: PlaylistDAO, playlist_id: str, song_id: str):
    names = ["add_song_to_playlist", "add_song", "attach_song"]
    for n in names:
        if hasattr(playlist_dao, n):
            try:
                res = getattr(playlist_dao, n)(playlist_id, song_id)
                return True
            except Exception:
                pass
    try:
        r = supabase.table("playlist_songs").insert({"playlist_id": playlist_id, "song_id": song_id}).execute()
        return bool(getattr(r, "data", None))
    except Exception:
        return False

def remove_song_from_playlist_flexible(playlist_dao: PlaylistDAO, playlist_id: str, song_id: str):
    names = ["remove_song_from_playlist", "remove_song", "detach_song"]
    for n in names:
        if hasattr(playlist_dao, n):
            try:
                res = getattr(playlist_dao, n)(playlist_id, song_id)
                return True
            except Exception:
                pass
    try:
        r = supabase.table("playlist_songs").delete().eq("playlist_id", playlist_id).eq("song_id", song_id).execute()
        return bool(getattr(r, "data", None))
    except Exception:
        return False

def get_songs_in_playlist_flexible(playlist_song_dao: PlaylistSongDAO, playlist_dao: PlaylistDAO, playlist_id: str):
    tries = [
        (playlist_song_dao, "list_songs_in_playlist"),
        (playlist_song_dao, "get_songs_in_playlist"),
        (playlist_dao, "get_songs_in_playlist"),
        (playlist_dao, "list_songs_in_playlist"),
    ]
    for obj, name in tries:
        if hasattr(obj, name):
            try:
                res = getattr(obj, name)(playlist_id)
                data = _data_of(res)
                if data is not None:
                    return data if isinstance(data, list) else [data]
            except Exception:
                pass
    # fallback: manual join
    try:
        ps = supabase.table("playlist_songs").select("song_id").eq("playlist_id", playlist_id).execute()
        ids = [r["song_id"] for r in (ps.data or []) if r.get("song_id")]
        if not ids:
            return []
        songs = supabase.table("songs").select("*").in_("song_id", ids).execute()
        return songs.data or []
    except Exception:
        return []

# -------------------------
# Auth helpers & UI
# -------------------------
def ensure_auth_state():
    if "auth" not in st.session_state:
        st.session_state.auth = {"user": None, "email": None, "role": None}

def ensure_profile_and_sync(user_id: str, email: str):
    """Ensure the users table has a row for this auth user_id. If email exists, update user_id to avoid FK errors."""
    try:
        resp = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if resp.data:
            return
        # If email exists but different user_id, update that row to have this user_id
        resp2 = supabase.table("users").select("*").eq("email", email).maybe_single().execute()
        if getattr(resp2, "data", None):
            existing = resp2.data
            # if existing has no user_id or different, update it
            supabase.table("users").update({"user_id": user_id}).eq("email", email).execute()
            return
        # otherwise insert new
        supabase.table("users").insert({
            "user_id": user_id,
            "email": email,
            "username": (email or "").split("@")[0],
            "role": "User"
        }).execute()
    except Exception as e:
        print("ensure_profile_and_sync() error:", e)

def sign_in(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = getattr(res, "user", None) or (getattr(res, "data", {}) or {}).get("user")
        sess = getattr(res, "session", None) or (getattr(res, "data", {}) or {}).get("session")
        if user and getattr(user, "id", None):
            ensure_profile_and_sync(user.id, email)
            role_resp = supabase.table("users").select("role").eq("user_id", user.id).maybe_single().execute()
            role = role_resp.data.get("role") if getattr(role_resp, "data", None) else "User"
            st.session_state.auth = {"user": {"id": user.id}, "email": email, "role": role}
            st.success("Signed in.")
            st.rerun()
        else:
            st.error("Sign-in failed.")
    except Exception as e:
        st.error(f"Sign-in error: {e}")

def sign_up(email: str, password: str):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        user = getattr(res, "user", None) or (getattr(res, "data", {}) or {}).get("user")
        if user and getattr(user, "id", None):
            ensure_profile_and_sync(user.id, email)
            st.success("Account created — verify email if your Supabase is configured for confirmation.")
        else:
            st.error("Sign-up returned no user id (check Supabase response).")
    except Exception as e:
        st.error(f"Sign-up error: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.auth = {"user": None, "email": None, "role": None}
    st.rerun()

# -------------------------
# Pages (Playlists is the full-featured one)
# -------------------------
def playlists_page():
    st.header("🎵 Playlists — Manage your playlists")
    playlist_dao = PlaylistDAO()
    playlist_song_dao = PlaylistSongDAO()
    song_dao = SongDAO()
    mood_dao = MoodDAO()

    user_id = st.session_state.auth["user"]["id"]

    # Create block
    with st.expander("➕ Create New Playlist", expanded=False):
        name = st.text_input("Playlist name", key="create_name")
        desc = st.text_area("Description", key="create_desc")
        # moods list (fallback to all moods if per-user not available)
        moods = _data_of(mood_dao.get_moods_by_user(user_id) if hasattr(mood_dao, "get_moods_by_user") else (mood_dao.list_moods() if hasattr(mood_dao, "list_moods") else [])) or []
        mood_map = {m.get("mood_name", m.get("name","")): m.get("mood_id") for m in moods if m.get("mood_id")}
        selected_mood_name = st.selectbox("Mood (optional)", [""] + list(mood_map.keys()), key="create_mood")
        if st.button("Create Playlist", key="btn_create_playlist"):
            if not name:
                st.warning("Enter playlist name.")
            else:
                created = create_playlist_flexible(playlist_dao, user_id, name, desc or "", mood_map.get(selected_mood_name))
                if created:
                    st.success("Playlist created.")
                    st.rerun()
                else:
                    st.error("Create failed. Check console for details.")

    st.markdown("---")

    # Search + list
    search = st.text_input("🔎 Search playlists by name", key="search_playlists")
    playlists = list_playlists_for_user(playlist_dao, user_id) or []

    # normalize name keys
    def _playlist_name(p):
        for k in ("playlist_name", "name", "title"):
            if k in p:
                return p[k]
        return "<Unnamed>"

    if search:
        playlists = [p for p in playlists if search.lower() in str(_playlist_name(p)).lower()]

    if not playlists:
        st.info("No playlists yet.")
        return

    # Build display table with consistent columns
    rows = []
    for p in playlists:
        pid = p.get("playlist_id") or p.get("id") or p.get("playlistId")
        rows.append({
            "playlist_id": pid,
            "name": _playlist_name(p),
            "created_at": p.get("created_at") or p.get("createdAt") or ""
        })
    df = pd.DataFrame(rows)
    df_display = df.rename(columns={"playlist_id": "Playlist ID", "name": "Name", "created_at": "Created At"})
    st.dataframe(df_display, width='stretch')

    # Select playlist to manage
    selected_id = st.selectbox("Select playlist to manage", [""] + list(df["playlist_id"].astype(str)), key="select_playlist_manage")
    if not selected_id:
        return

    selected_record = next((p for p in playlists if (p.get("playlist_id") == selected_id or str(p.get("playlist_id")) == str(selected_id) or p.get("id") == selected_id)), None)
    st.markdown(f"### ⚙️ Manage: **{_playlist_name(selected_record) if selected_record else selected_id}**")

    # Update
    with st.expander("✏️ Update playlist", expanded=False):
        cur_name = _playlist_name(selected_record) if selected_record else ""
        new_name = st.text_input("New name", value=cur_name, key="update_name")
        new_desc = st.text_area("New description", value=selected_record.get("description","") if selected_record else "", key="update_desc")
        # mood options again
        mood_choice = st.selectbox("Mood (optional)", [""] + list(mood_map.keys()), key="update_mood")
        if st.button("Update Playlist", key="btn_update_playlist"):
            ok = update_playlist_flexible(playlist_dao, selected_id, user_id=user_id, name=new_name, description=new_desc, mood_id=mood_map.get(mood_choice))
            if ok:
                st.success("Playlist updated.")
                st.rerun()
            else:
                st.error("Update failed.")

    # Delete
    with st.expander("🚨 Delete playlist", expanded=False):
        if st.button("Delete playlist", key="btn_delete_playlist"):
            ok = delete_playlist_flexible(playlist_dao, selected_id, user_id)
            if ok:
                st.success("Deleted.")
                st.rerun()
            else:
                st.error("Delete failed.")

    st.markdown("---")

    # Songs in playlist (view/remove)
    st.subheader("🎧 Songs in playlist")
    songs_in = get_songs_in_playlist_flexible(playlist_song_dao, playlist_dao, selected_id) or []
    if songs_in:
        # prefer columns title/song_id
        srows = []
        for s in songs_in:
            sid = s.get("song_id") or s.get("id") or s.get("songId")
            title = s.get("title") or s.get("name") or s.get("song_name") or ""
            srows.append({"song_id": sid, "title": title})
        st.dataframe(pd.DataFrame(srows), use_container_width=True)

        remove_map = {f"{r['title']} — {r['song_id']}": r['song_id'] for r in srows}
        to_remove_label = st.selectbox("Select song to remove", list(remove_map.keys()), key="select_song_remove")
        if st.button("Remove song from playlist", key="btn_remove_song"):
            sid = remove_map[to_remove_label]
            ok = remove_song_from_playlist_flexible(playlist_dao, selected_id, sid)
            if ok:
                st.success("Removed song.")
                st.rerun()
            else:
                st.error("Remove failed.")
    else:
        st.info("No songs in this playlist.")

    st.markdown("---")

    # Add song to playlist
    st.subheader("➕ Add song to playlist")
    all_songs = _data_of(song_dao.list_songs() if hasattr(song_dao, "list_songs") else []) or []
    if not all_songs:
        st.info("No songs available (create songs in Songs module).")
    else:
        add_map = { (s.get("title") or s.get("name") or s.get("song_name") or "") + " — " + str(s.get("song_id") or s.get("id")): (s.get("song_id") or s.get("id")) for s in all_songs }
        add_choice = st.selectbox("Select song to add", list(add_map.keys()), key="select_song_add")
        if st.button("Add song to playlist", key="btn_add_song"):
            sid = add_map[add_choice]
            ok = add_song_to_playlist_flexible(playlist_dao, selected_id, sid)
            if ok:
                st.success("Song added.")
                st.rerun()
            else:
                st.error("Add failed.")
def playlists_by_mood_page():
    st.markdown("<h2 style='color:#007bff;'>🎵 Playlists by Mood</h2>", unsafe_allow_html=True)
    st.write("Select a mood to see playlists associated with it.")

    mood_dao = MoodDAO()
    playlist_dao = PlaylistDAO()

    # Get logged-in user
    user_id = st.session_state.auth.get("user_id")

    try:
        moods = mood_dao.get_moods_by_user(user_id)
    except Exception as e:
        st.error(f"Error fetching moods: {e}")
        return

    if not moods:
        st.info("No moods found. Please create one first.")
        return

    # Dropdown for mood selection
    mood_options = {m["mood_name"]: m["mood_id"] for m in moods}
    selected_mood_name = st.selectbox("Select a Mood 🎧", list(mood_options.keys()))

    if selected_mood_name:
        selected_mood_id = mood_options[selected_mood_name]

        try:
            playlists = playlist_dao.get_playlists_by_mood(selected_mood_id)
        except Exception as e:
            st.error(f"Error fetching playlists: {e}")
            return

        if playlists:
            st.markdown(f"### 🎶 Playlists for *{selected_mood_name}* mood")

            for p in playlists:
                with st.container():
                    st.markdown(
                        f"""
                        <div class="playlist-card">
                            <strong>🎵 {p.get('playlist_name', 'Unnamed')}</strong><br>
                            <small>Created At: {p.get('created_at', 'N/A')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.warning(f"No playlists found for mood **{selected_mood_name}**.")




# -------------------------
# Simpler pages (Moods, Songs, Artists, Users, Reports)
# -------------------------
def moods_page():
    st.header("🧭 Moods")
    mood_dao = MoodDAO()
    user_id = st.session_state.auth["user"]["id"]
    # Create
    with st.form("create_mood"):
        mname = st.text_input("Mood name")
        mdesc = st.text_area("Description")
        if st.form_submit_button("Create Mood"):
            try:
                # try signature with user_id first
                try:
                    mood_dao.create_mood(user_id, mname, mdesc)
                except TypeError:
                    mood_dao.create_mood(mname, mdesc)
                st.success("Mood created.")
                st.rerun()
            except Exception as e:
                st.error(f"Create failed: {e}")

    # List & search
    moods = _data_of(mood_dao.get_moods_by_user(user_id) if hasattr(mood_dao, "get_moods_by_user") else (mood_dao.list_moods() if hasattr(mood_dao, "list_moods") else [])) or []
    if moods:
        df = pd.DataFrame(moods)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No moods found.")

def songs_page():
    st.header("🎵 Songs")
    song_dao = SongDAO()
    # Create
    with st.form("create_song"):
        title = st.text_input("Title")
        duration = st.number_input("Duration (seconds)", min_value=0)
        if st.form_submit_button("Create Song"):
            try:
                try:
                    song_dao.create_song(title, duration)
                except TypeError:
                    song_dao.create_song(None, title, duration)
                st.success("Song created.")
                st.rerun()
            except Exception as e:
                st.error(f"Create failed: {e}")

    songs = _data_of(song_dao.list_songs() if hasattr(song_dao, "list_songs") else [])
    if songs:
        st.dataframe(pd.DataFrame(songs), use_container_width=True)
    else:
        st.info("No songs found.")
def logout_page():
    """
    Simple logout UI. Uses existing sign_out() if available.
    If sign_out() isn't defined for some reason, this clears the session state
    and forces a rerun.
    """
    st.header("🔒 Logout")

    # show current user (if available)
    auth = st.session_state.get("auth", {})
    email = auth.get("email") if isinstance(auth, dict) else None
    if email:
        st.write(f"Signed in as: **{email}**")
    else:
        st.write("You are not signed in.")

    st.write("Click the button below to sign out.")

    if st.button("Sign out", key="logout_btn"):
        # Prefer using your existing sign_out() helper (it should clear state and rerun)
        try:
            sign_out()
        except NameError:
            # fallback: clear auth state ourselves and rerun
            st.session_state.auth = {"user": None, "email": None, "role": None}
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                # Old Streamlit versions:
                try:
                    st.experimental_rerun()
                except Exception:
                    pass

        # If sign_out didn't rerun immediately, show feedback
        st.success("Signed out.")


def artists_page():
    st.header("🎤 Artists")
    artist_dao = ArtistDAO()
    user_id = st.session_state.auth["user"]["id"]
    with st.form("create_artist"):
        name = st.text_input("Artist name")
        desc = st.text_area("Description")
        if st.form_submit_button("Create Artist"):
            try:
                try:
                    artist_dao.create_artist(user_id, name, desc)
                except TypeError:
                    artist_dao.create_artist(name, desc)
                st.success("Artist created.")
                st.rerun()
            except Exception as e:
                st.error(f"Create failed: {e}")
    artists = _data_of(artist_dao.list_artists() if hasattr(artist_dao, "list_artists") else [])
    if artists:
        st.dataframe(pd.DataFrame(artists), use_container_width=True)
    else:
        st.info("No artists found.")

def users_page():
    st.header("👥 Users (Admin)")
    user_dao = UserDAO()
    with st.form("create_user_admin"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["User", "Admin"])
        if st.form_submit_button("Create User"):
            try:
                pw_hash = hash_password(password)
                user_dao.create_user(username, email, pw_hash, role)
                st.success("User created.")
                st.rerun()
            except Exception as e:
                st.error(f"Create failed: {e}")
    users = _data_of(user_dao.list_all_users() if hasattr(user_dao, "list_all_users") else [])
    if users:
        st.dataframe(pd.DataFrame(users), use_container_width=True)
    else:
        st.info("No users found.")

def reports_page():
    st.header("📊 Reports")
    repo = ReportDAO()
    try:
        urole = _data_of(repo.count_users_by_role() if hasattr(repo, "count_users_by_role") else [])
        st.subheader("Users by role")
        if urole:
            st.dataframe(pd.DataFrame(urole))
        else:
            st.info("No data.")
        pm = _data_of(repo.count_playlists_by_mood() if hasattr(repo, "count_playlists_by_mood") else [])
        st.subheader("Playlists by mood")
        if pm:
            st.dataframe(pd.DataFrame(pm))
        else:
            st.info("No data.")
    except Exception as e:
        st.error(f"Report error: {e}")

# -------------------------
# Login screen + main
# -------------------------
def login_screen():
    st.title("Mood-Based Playlist Manager")
    st.markdown("Welcome — sign in or register.")
    tab1, tab2 = st.tabs(["Sign in", "Register"])
    with tab1:
        with st.form("signin"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in"):
                sign_in(email, password)
    with tab2:
        with st.form("signup"):
            email_r = st.text_input("Email (register)", key="reg_email")
            password_r = st.text_input("Password", type="password", key="reg_pass")
            if st.form_submit_button("Register"):
                sign_up(email_r, password_r)

def main():
    st.set_page_config(page_title="Mood-Based Playlist Manager", layout="wide")

    # 🎨 Custom Styles
    st.markdown("""
        <style>
        /* Main background */
        body, .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important;
            color: white !important;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #007bff !important;
        }

        /* Buttons */
        .stButton>button {
            background-color: #007bff;
            color: white;
            border-radius: 10px;
            padding: 0.5em 1.2em;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }

        /* Cards */
        .playlist-card {
            background-color: #1c1c1c;
            color: #ffffff;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            box-shadow: 0 0 10px rgba(0,0,255,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    #print("✅ Updated version deployed")


    # Initialize authentication state
    ensure_auth_state()

    # 🔐 If not logged in, show login/register
    if not st.session_state.auth.get("user"):
        login_screen()
        return

    # 🧭 Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.caption(f"Signed in as: {st.session_state.auth.get('email')}")
    role = st.session_state.auth.get("role", "User")

    pages = ["Moods", "Playlists", "Songs", "Playlists by Mood", "Logout"]
    if role == "Admin":
        pages.insert(0, "Users")

    choice = st.sidebar.radio("Go to", pages)

    # 🧱 Routing
    if choice == "Moods":
        moods_page()
    elif choice == "Playlists":
        playlists_page()
    elif choice == "Songs":
        songs_page()
    elif choice == "Playlists by Mood":
        playlists_by_mood_page()
    elif choice == "Users":
        users_page()
    elif choice == "Logout":
        logout_page()
    else:
        st.info("Choose a page from the sidebar.")


if __name__ == "__main__":
    main()
