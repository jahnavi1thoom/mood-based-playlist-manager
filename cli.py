from dao.user_dao import UserDAO
from dao.playlist_dao import PlaylistDAO
from dao.mood_dao import MoodDAO
from dao.playlist_song_dao import PlaylistSongDAO
from dao.song_dao import SongDAO
from dao.artist_dao import ArtistDAO  # Added import for ArtistDAO
from dao.report_dao import ReportDAO

import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def user_menu(user_dao):
    while True:
        print("\nMood-Based Playlist Manager — User Management")
        print("1. Create User")
        print("2. Get User by Email")
        print("3. Update User Role")
        print("4. Delete User")
        print("5. List All Users")
        print("6. Back to Main Menu")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            role = input("Enter role (User/Admin) [default User]: ").strip() or "User"
            password_hash = hash_password(password)
            user = user_dao.create_user(username, email, password_hash, role)
            if user:
                print(f"User created successfully! User ID: {user['user_id']}")
            else:
                print("Error creating user.")

        elif choice == "2":
            email = input("Enter user email: ").strip()
            user = user_dao.get_user_by_email(email)
            if user:
                print(f"User found: {user}")
            else:
                print("User not found.")

        elif choice == "3":
            user_id = input("Enter user ID to update role: ").strip()
            new_role = input("Enter new role (User/Admin): ").strip()
            if user_dao.update_user_role(user_id, new_role):
                print("User role updated successfully.")
            else:
                print("Failed to update role.")

        elif choice == "4":
            user_id = input("Enter user ID to delete: ").strip()
            confirm = input("Are you sure? This action cannot be undone (y/n): ").strip().lower()
            if confirm == "y":
                if user_dao.delete_user(user_id):
                    print("User deleted successfully.")
                else:
                    print("Failed to delete user.")
            else:
                print("Delete cancelled.")

        elif choice == "5":
            users = user_dao.list_all_users()
            print(f"Total users: {len(users)}")
            for u in users:
                print(f"- ID: {u['user_id']}, Username: {u['username']}, Email: {u['email']}, Role: {u['role']}")

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

def playlist_menu(playlist_dao):
    while True:
        print("\nPlaylist Management")
        print("1. Create Playlist")
        print("2. Get Playlist by ID")
        print("3. Update Playlist")
        print("4. Delete Playlist")
        print("5. List All Playlists")
        print("6. Back to Main Menu")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            user_id = input("Enter User ID who owns the playlist: ").strip()
            name = input("Enter Playlist Name: ").strip()
            description = input("Enter Description (optional): ").strip()
            mood_id_input = input("Enter Mood ID (optional): ").strip()
            mood_id = mood_id_input if mood_id_input else None
            playlist = playlist_dao.create_playlist(user_id, name, description, mood_id)
            if playlist:
                print(f"Playlist created! Playlist ID: {playlist['playlist_id']}")
            else:
                print("Failed to create playlist.")

        elif choice == "2":
            playlist_id = input("Enter Playlist ID: ").strip()
            playlist = playlist_dao.get_playlist_by_id(playlist_id)
            if playlist:
                print(playlist)
            else:
                print("Playlist not found.")

        elif choice == "3":
            playlist_id = input("Enter Playlist ID to update: ").strip()
            print("Press Enter to skip updating a field.")
            name = input("New Playlist Name: ").strip() or None
            description = input("New Description: ").strip() or None
            mood_id_input = input("New Mood ID: ").strip()
            mood_id = mood_id_input if mood_id_input else None
            updated = playlist_dao.update_playlist(playlist_id, name, description, mood_id)
            print("Playlist updated." if updated else "Update failed.")

        elif choice == "4":
            playlist_id = input("Enter Playlist ID to delete: ").strip()
            confirm = input("Are you sure? This action cannot be undone (y/n): ").strip().lower()
            if confirm == "y":
                deleted = playlist_dao.delete_playlist(playlist_id)
                print("Playlist deleted." if deleted else "Delete failed.")
            else:
                print("Delete cancelled.")

        elif choice == "5":
            playlists = playlist_dao.list_playlists()
            print(f"Total playlists: {len(playlists)}")
            for pl in playlists:
                print(f"- ID: {pl['playlist_id']}, Name: {pl['name']}, User ID: {pl['user_id']}, Mood ID: {pl.get('mood_id')}")

        elif choice == "6":
            break

        else:
            print("Invalid choice, please select 1-6.")

def mood_menu(mood_dao):
    while True:
        print("\nMood Management")
        print("1. Create Mood")
        print("2. Get Mood by ID")
        print("3. Update Mood")
        print("4. Delete Mood")
        print("5. List All Moods")
        print("6. Back to Main Menu")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            mood_name = input("Enter Mood Name: ").strip()
            description = input("Enter Description (optional): ").strip()
            mood = mood_dao.create_mood(mood_name, description)
            if mood:
                print(f"Mood created! Mood ID: {mood['mood_id']}")
            else:
                print("Failed to create mood.")

        elif choice == "2":
            mood_id = input("Enter Mood ID: ").strip()
            mood = mood_dao.get_mood_by_id(mood_id)
            if mood:
                print(mood)
            else:
                print("Mood not found.")

        elif choice == "3":
            mood_id = input("Enter Mood ID to update: ").strip()
            print("Press Enter to skip updating a field.")
            mood_name = input("New Mood Name: ").strip() or None
            description = input("New Description: ").strip() or None
            updated = mood_dao.update_mood(mood_id, mood_name, description)
            print("Mood updated." if updated else "Update failed.")

        elif choice == "4":
            mood_id = input("Enter Mood ID to delete: ").strip()
            confirm = input("Are you sure? This action cannot be undone (y/n): ").strip().lower()
            if confirm == "y":
                deleted = mood_dao.delete_mood(mood_id)
                print("Mood deleted." if deleted else "Delete failed.")
            else:
                print("Delete cancelled.")

        elif choice == "5":
            moods = mood_dao.list_moods()
            print(f"Total moods: {len(moods)}")
            for m in moods:
                print(f"- ID: {m['mood_id']}, Name: {m['mood_name']}, Description: {m['description']}")

        elif choice == "6":
            break

        else:
            print("Invalid choice, please select 1-6.")

def playlist_song_menu(playlist_song_dao):
    while True:
        print("\nManage Songs in Playlists")
        print("1. Add Song to Playlist")
        print("2. Remove Song from Playlist")
        print("3. List Songs in Playlist")
        print("4. Back to Main Menu")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            playlist_id = input("Enter Playlist ID: ").strip()
            song_id = input("Enter Song ID to add: ").strip()
            if playlist_song_dao.add_song_to_playlist(playlist_id, song_id):
                print("Song added to playlist.")
            else:
                print("Failed to add song.")

        elif choice == "2":
            playlist_id = input("Enter Playlist ID: ").strip()
            song_id = input("Enter Song ID to remove: ").strip()
            if playlist_song_dao.remove_song_from_playlist(playlist_id, song_id):
                print("Song removed from playlist.")
            else:
                print("Failed to remove song.")

        elif choice == "3":
            playlist_id = input("Enter Playlist ID to list songs: ").strip()
            songs = playlist_song_dao.list_songs_in_playlist(playlist_id)
            if songs:
                print(f"Songs in playlist {playlist_id}:")
                for s in songs:
                    print(f"- Song ID: {s['song_id']}")
            else:
                print("No songs found or playlist is empty.")

        elif choice == "4":
            break

        else:
            print("Invalid choice. Please select 1-4.")

def song_menu(song_dao):
    while True:
        print("\nSong Management")
        print("1. Create Song")
        print("2. Get Song by ID")
        print("3. Update Song")
        print("4. Delete Song")
        print("5. List All Songs")
        print("6. Back to Main Menu")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            title = input("Enter Song Title: ").strip()
            duration_input = input("Enter Duration in seconds (optional): ").strip()
            duration = int(duration_input) if duration_input.isdigit() else None
            artist_id = input("Enter Artist ID (optional): ").strip() or None
            genre_id = input("Enter Genre ID (optional): ").strip() or None
            song = song_dao.create_song(title, duration, artist_id, genre_id)
            if song:
                print(f"Song created! Song ID: {song['song_id']}")
            else:
                print("Failed to create song.")

        elif choice == "2":
            song_id = input("Enter Song ID: ").strip()
            song = song_dao.get_song_by_id(song_id)
            if song:
                print(song)
            else:
                print("Song not found.")

        elif choice == "3":
            song_id = input("Enter Song ID to update: ").strip()
            print("Press Enter to skip updating a field.")
            title = input("New Title: ").strip() or None
            duration_input = input("New Duration in seconds: ").strip()
            duration = int(duration_input) if duration_input.isdigit() else None
            artist_id = input("New Artist ID (optional): ").strip() or None
            genre_id = input("New Genre ID (optional): ").strip() or None
            updated = song_dao.update_song(song_id, title, duration, artist_id, genre_id)
            print("Song updated." if updated else "Update failed.")

        elif choice == "4":
            song_id = input("Enter Song ID to delete: ").strip()
            confirm = input("Are you sure? This action cannot be undone (y/n): ").strip().lower()
            if confirm == "y":
                deleted = song_dao.delete_song(song_id)
                print("Song deleted." if deleted else "Delete failed.")
            else:
                print("Delete cancelled.")

        elif choice == "5":
            songs = song_dao.list_songs()
            print(f"Total songs: {len(songs)}")
            for s in songs:
                print(f"- ID: {s['song_id']}, Title: {s['title']}, Duration: {s.get('duration')} sec, Artist ID: {s.get('artist_id')}, Genre ID: {s.get('genre_id')}")

        elif choice == "6":
            break

        else:
            print("Invalid choice, please select 1-6.")

def artist_menu(artist_dao):
    while True:
        print("\nArtist Management")
        print("1. Create Artist")
        print("2. Get Artist by ID")
        print("3. Update Artist")
        print("4. Delete Artist")
        print("5. List All Artists")
        print("6. Back to Main Menu")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            name = input("Enter Artist Name: ").strip()
            description = input("Enter Description (optional): ").strip()
            artist = artist_dao.create_artist(name, description)
            if artist:
                print(f"Artist created! Artist ID: {artist['artist_id']}")
            else:
                print("Failed to create artist.")

        elif choice == "2":
            artist_id = input("Enter Artist ID: ").strip()
            artist = artist_dao.get_artist_by_id(artist_id)
            if artist:
                print(artist)
            else:
                print("Artist not found.")

        elif choice == "3":
            artist_id = input("Enter Artist ID to update: ").strip()
            print("Press Enter to skip updating a field.")
            name = input("New Artist Name: ").strip() or None
            description = input("New Description: ").strip() or None
            updated = artist_dao.update_artist(artist_id, name, description)
            print("Artist updated." if updated else "Update failed.")

        elif choice == "4":
            artist_id = input("Enter Artist ID to delete: ").strip()
            confirm = input("Are you sure? This action cannot be undone (y/n): ").strip().lower()
            if confirm == "y":
                deleted = artist_dao.delete_artist(artist_id)
                print("Artist deleted." if deleted else "Delete failed.")
            else:
                print("Delete cancelled.")

        elif choice == "5":
            artists = artist_dao.list_artists()
            print(f"Total artists: {len(artists)}")
            for a in artists:
                print(f"- ID: {a['artist_id']}, Name: {a['name']}, Description: {a.get('description')}")

        elif choice == "6":
            break

        else:
            print("Invalid choice, please select 1-6.")
def report_menu(report_dao):
    while True:
        print("\nReports Menu")
        print("1. User Count by Role")
        print("2. Playlist Count by Mood")
        print("3. Back to Main Menu")

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            data = report_dao.count_users_by_role()
            if data:
                print("User counts by role:")
                for item in data:
                    print(f"- Role: {item['role']}, Count: {item['count']}")
            else:
                print("No data available.")

        elif choice == "2":
            data = report_dao.count_playlists_by_mood()
            if data:
                    print("Playlist counts by mood:")
                    for item in data:
                        print(f"- Mood ID: {item['mood_id']}, Count: {item['count']}")
            else:
                    print("No data available.")

        elif choice == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def main_menu():
    user_dao = UserDAO()
    playlist_dao = PlaylistDAO()
    mood_dao = MoodDAO()
    playlist_song_dao = PlaylistSongDAO()
    song_dao = SongDAO()
    artist_dao = ArtistDAO()
    report_dao = ReportDAO()  # Initialize ReportDAO

    while True:
        print("\nMood-Based Playlist Manager")
        print("1. User Management")
        print("2. Playlist Management")
        print("3. Mood Management")
        print("4. Manage Songs in Playlists")
        print("5. Song Management")
        print("6. Artist Management")
        print("7. Reports")
        print("8. Exit")

        choice = input("Enter choice (1-8): ").strip()

        if choice == "1":
            user_menu(user_dao)
        elif choice == "2":
            playlist_menu(playlist_dao)
        elif choice == "3":
            mood_menu(mood_dao)
        elif choice == "4":
            playlist_song_menu(playlist_song_dao)
        elif choice == "5":
            song_menu(song_dao)
        elif choice == "6":
            artist_menu(artist_dao)
        elif choice == "7":
            report_menu(report_dao)
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")



if __name__ == "__main__":
    main_menu()
