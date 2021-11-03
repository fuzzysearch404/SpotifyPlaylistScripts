import argparse
import spotipy
import secrets as user_secrets
from spotipy.oauth2 import SpotifyOAuth


PERMISSIONS_SCOPE = 'user-library-read playlist-modify-public playlist-modify-private'

TRACK_IDS = None
IGNORE_PLAYLIST_IDS = None


def get_args():
    parser = argparse.ArgumentParser(description='Deletes songs from all user playlists.', add_help=True)
    parser.add_argument('track_ids', nargs='+',
                        help='Track IDs of the track that will be removed from all your playlists. Required.')
    parser.add_argument('-i', '--ignore-playlists', nargs='+',
                        help='Playlist IDs of playlists that will be ignored.')
    return parser.parse_args()


def main():
    if not TRACK_IDS:
        raise Exception("Atleast one track ID is required.")

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

    user_playlists = spotify_client.current_user_playlists(limit=50)
    if not user_playlists:
        raise Exception("Failed to playlists or user has no playlists.")

    def remove_track_from_playlists(playlists_data):
        for playlist in playlists_data['items']:
            if playlist['id'] in IGNORE_PLAYLIST_IDS:
                print(f"Skipping playlist: {playlist['name']}")
                continue
            if playlist['owner']['id'] == current_user['id']:
                print(f"Removing tracks {TRACK_IDS} from playlist: {playlist['name']}")
                spotify_client.playlist_remove_all_occurrences_of_items(playlist['id'], TRACK_IDS)

    remove_track_from_playlists(user_playlists)
    while user_playlists['next']:
        user_playlists = spotify_client.next(user_playlists)
        remove_track_from_playlists(user_playlists)

    print("Done.")


if __name__ == '__main__':
    args = get_args()
    TRACK_IDS = args.track_ids
    IGNORE_PLAYLIST_IDS = args.ignore_playlists or ()

    main()
