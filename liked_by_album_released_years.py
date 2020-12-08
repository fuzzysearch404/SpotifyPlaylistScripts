import argparse
import spotipy
import secrets as user_secrets
from spotipy.oauth2 import SpotifyOAuth


PERMISSIONS_SCOPE = 'user-library-read playlist-modify-public'

START_YEAR, END_YEAR = -1, -1

# Track stats
FILTERED, ADDED, SKIPPED = 0, 0, 0


def get_args():
    parser = argparse.ArgumentParser(description='Creates a playlist for user.', add_help=True)
    parser.add_argument('-s', '--start-year', required=True, type=int,
                        help='Starting release year for liked songs to filter. Required.')
    parser.add_argument('-e', '--end-year', required=True, type=int,
                        help='Ending release year for liked songs to filter. Required.')
    return parser.parse_args()

def track_should_be_added(track):
    album = track['album']
    date_unparsed = album["release_date"]

    try:
        year = int(date_unparsed.split("-")[0]) # Expected formats: 2020-01-01, 2020-01, 2020
    except Exception:
        return False
    
    return year >= START_YEAR and year <= END_YEAR

def filter_tracks_to_list(to_add, results):
    global FILTERED, SKIPPED

    for item in results['items']:
        FILTERED += 1
        track = item['track']
        if track_should_be_added(track):
            print("Adding: %32.32s %s" % (track['artists'][0]['name'], track['name']))
            to_add.append(track['id'])
        else:
            SKIPPED += 1

def main():
    global FILTERED, ADDED, SKIPPED

    if START_YEAR < 0 or END_YEAR < 0:
        raise Exception("Only positive year integers are allowed.")
    if START_YEAR > 2100 or END_YEAR > 2100:
        raise Exception("I think that we are not there yet, buddy.")
    if START_YEAR > END_YEAR:
        raise Exception("End year cannot be greater than start year.")

    authorization = SpotifyOAuth(
        scope=PERMISSIONS_SCOPE,
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
        description="Automatically generated with https://github.com/fuzzysearch404/SpotifyPlaylistScripts"
    )
    if not created_playlist:
        raise Exception("Failed to create a playlist.")

    print(f"Playlist created. ID:{created_playlist['id']}")

    results = spotify_client.current_user_saved_tracks(limit=50)
    if not results:
        raise Exception("Failed to load liked songs or user has no liked songs.")

    to_add = []

    def add_tracks_to_spotify_playlist():
        print(f"Sending a request to Spotify to add {len(to_add)} tracks.")
        spotify_client.playlist_add_items(created_playlist['id'], to_add)
    
    filter_tracks_to_list(to_add, results)
    while results['next']:
        results = spotify_client.next(results)
        filter_tracks_to_list(to_add, results)

        # Limit list of songs to be added at a time to about 50 from max 100.
        if len(to_add) >= 50:
            add_tracks_to_spotify_playlist()
            ADDED += len(to_add)
            to_add = []

    if len(to_add) > 0:
        add_tracks_to_spotify_playlist()
        ADDED += len(to_add)

    print("Done.")
    print(f"Filtered: {FILTERED}, Added: {ADDED}, Skipped: {SKIPPED}")

if __name__ == '__main__':
    args = get_args()
    START_YEAR = args.start_year
    END_YEAR = args.end_year

    main()