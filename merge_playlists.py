import argparse
import spotipy
import secrets as user_secrets
from spotipy.oauth2 import SpotifyOAuth


PERMISSIONS_SCOPE = "user-library-read playlist-modify-public playlist-modify-private"

PLAYLIST_IDS = None
APPEND_PLAYLIST_ID = None


def get_args():
    parser = argparse.ArgumentParser(description="Merges playlists, by creating a combined playlist", add_help=True)
    parser.add_argument("playlist_ids", nargs="+",
                        help="Playlist IDs of playlists to merge together. Required.")
    parser.add_argument("-a", "--append-playlist",
                        help="Rather than creating a new playlist for the merged playlists, append an existing one.")

    return parser.parse_args()


def main():
    if not PLAYLIST_IDS:
        raise Exception("Atleast one playlist ID is required.")

    authorization = SpotifyOAuth(
        scope=PERMISSIONS_SCOPE,
        client_id=user_secrets.CLIENT_ID,
        client_secret=user_secrets.CLIENT_SECRET,
        redirect_uri=user_secrets.REDIRECT_URI,
        open_browser=False
    )

    spotify_client = spotipy.Spotify(auth_manager=authorization)
    current_user = spotify_client.me()
    if not spotify_client or not current_user:
        raise Exception("Failed to authorize app client or user.")

    print(f"Authorized as: {current_user['display_name']}")

    if not APPEND_PLAYLIST_ID:
        created_playlist = spotify_client.user_playlist_create(
            user=current_user['id'],
            name="My merged playlist",
            description="Automatically generated with https://github.com/fuzzysearch404/SpotifyPlaylistScripts"
            f" | Merged from {len(PLAYLIST_IDS)} playlists"
        )
        if not created_playlist:
            raise Exception("Failed to create a playlist.")
        created_playlist_id = created_playlist['id']

        print(f"Playlist created. ID:{created_playlist_id}")

    resulting_playlist_id = APPEND_PLAYLIST_ID or created_playlist_id

    def add_tracks(res):
        to_add = [t['track']['id'] for t in res['items'] if t['track']['id'] is not None]
        print(f"Sending a request to bulk insert {len(to_add)} tracks into the new playlist")
        spotify_client.playlist_add_items(resulting_playlist_id, to_add)

    for playlist_id in PLAYLIST_IDS:
        results = spotify_client.playlist_items(playlist_id=playlist_id)
        add_tracks(results)

        while results['next']:
            results = spotify_client.next(results)
            add_tracks(results)

    print("Done.")


if __name__ == '__main__':
    args = get_args()
    PLAYLIST_IDS = args.playlist_ids or ()
    APPEND_PLAYLIST_ID = args.append_playlist

    main()
