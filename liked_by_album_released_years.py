import argparse
import spotipy
import secrets as user_secrets
import time
from spotipy.oauth2 import SpotifyOAuth

SCOPE = 'user-library-read playlist-modify-public'

START_YEAR, END_YEAR = -1, -1

# Stats
FILTERED, ADDED, SKIPPED = 0, 0, 0


def get_args():
    parser = argparse.ArgumentParser(description='Creates a playlist for user', add_help=True)
    parser.add_argument('-s', '--start-year', required=True, type=int,
                        help='Starting year for liked songs to filter')
    parser.add_argument('-e', '--end-year', required=True, type=int,
                        help='Ending year for liked songs to filter')
    return parser.parse_args()

def track_should_be_added(track):
    album = track['album']
    date_unparsed = album["release_date"]

    try:
        year = int(date_unparsed.split("-")[0])
    except Exception:
        return False
    
    return year >= START_YEAR and year <= END_YEAR

def add_tracks_to_playlist(spotify_client, results, playlist):
    global FILTERED, ADDED, SKIPPED
    FILTERED += len(results)
    to_add = []
    
    for item in results['items']:
        track = item['track']
        if track_should_be_added(track):
            print("Adding: %32.32s %s" % (track['artists'][0]['name'], track['name']))
            to_add.append(track['id'])
        else:
            SKIPPED += 1

    items_size = len(to_add)
    if items_size > 0:
        spotify_client.playlist_add_items(playlist, to_add)
        ADDED += items_size
    
        time.sleep(3) # I don't know what the ratelimits are, so we better be careful

def main():
    if START_YEAR < 0 or END_YEAR < 0:
        raise Exception("Only positive year integers are allowed.")
    if START_YEAR > 2100 or END_YEAR > 2100:
        raise Exception("I think where are not there yet buddy.")
    if START_YEAR > END_YEAR:
        raise Exception("End year cannot be greater than start year.")

    authorization = SpotifyOAuth(
        scope=SCOPE,
        client_id=user_secrets.CLIENT_ID,
        client_secret=user_secrets.CLIENT_SECRET,
        redirect_uri=user_secrets.REDIRECT_URI,
        open_browser=True
    )
    spotify_client = spotipy.Spotify(auth_manager=authorization)
    if not spotify_client.me():
        raise Exception("Failed to authorize app client or user.")

    print(f"Authorized as: {spotify_client.me()['display_name']}")

    created_playlist = spotify_client.user_playlist_create(
        user=spotify_client.me()['id'],
        name=f"My tracks {START_YEAR}-{END_YEAR}",
        description="Auto generated with https://github.com/fuzzysearch404/SpotifyPlaylistScripts"
    )
    if not created_playlist:
        raise Exception("Failed to create a playlist.")

    print(f"Playlist created. ID:{created_playlist['id']}")

    results = spotify_client.current_user_saved_tracks()
    if not results:
        raise Exception("Failed to load liked songs or user has no liked songs.")
    
    add_tracks_to_playlist(spotify_client, results, created_playlist['id'])
    while results['next']:
        results = spotify_client.next(results)
        add_tracks_to_playlist(spotify_client, results, created_playlist['id'])

    print("Done.")
    print(f"Filtered: {FILTERED}, Added: {ADDED}, Skipped: {SKIPPED}")

if __name__ == '__main__':
    args = get_args()
    START_YEAR = args.start_year
    END_YEAR = args.end_year

    main()