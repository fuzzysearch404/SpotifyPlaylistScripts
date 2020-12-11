import argparse
import spotipy
import secrets as user_secrets
from spotipy.oauth2 import SpotifyOAuth


PERMISSIONS_SCOPE = 'user-library-read playlist-modify-public'

FILTERS = None

# Track stats
FILTERED, ADDED, SKIPPED = 0, 0, 0


def get_args():
    parser = argparse.ArgumentParser(description='Creates a playlist for user.', add_help=True)
    # Argument descriptions source: 
    # https://developer.spotify.com/documentation/web-api/reference/tracks/get-several-audio-features/
    parser.add_argument('-a', '--min-acousticness', type=float,
                        help='Min. value. A confidence measure from 0.0 to 1.0 of whether the track is acoustic. '
                        '1.0 represents high confidence the track is acoustic.')
    parser.add_argument('-ma', '--max-acousticness', type=float,
                        help='Max. value for acousticness.')
    parser.add_argument('-d', '--min-danceability', type=float,
                        help='Min. value. Danceability describes how suitable a track is for dancing based on a '
                        'combination of musical elements including tempo, rhythm stability, beat strength, '
                        'and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.')
    parser.add_argument('-md', '--max-dancebillity', type=float,
                        help='Max. value for dancebillity.')
    parser.add_argument('-du', '--min-duration_ms', type=int,
                        help='Min. value. The duration of the track in milliseconds.')
    parser.add_argument('-mdu', '--max-duration_ms', type=int,
                        help='Max. value for duration_ms.')
    parser.add_argument('-e', '--min-energy', type=float,
                        help='Min. value. Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of '
                        'intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. '
                        'For example, death metal has high energy, while a Bach prelude scores low on the scale. '
                        'Perceptual features contributing to this attribute include dynamic range, '
                        'perceived loudness, timbre, onset rate, and general entropy.')
    parser.add_argument('-me', '--max-energy', type=float,
                        help='Max. value for energy.')
    parser.add_argument('-i', '--min-instrumentalness', type=float,
                        help='Min. value. Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as '
                        'instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the '
                        'instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. '
                        'Values above 0.5 are intended to represent instrumental tracks, but confidence '
                        'is higher as the value approaches 1.0.')
    parser.add_argument('-mi', '--max-instrumentalness', type=float,
                        help='Max. value for instrumentalness.')
    parser.add_argument('-k', '--min-key', type=int,
                        help='Min. value. The key the track is in. Integers map to pitches using standard Pitch Class notation. '
                        'E.g. 0 = C, 1 = C/D, 2 = D, and so on.')
    parser.add_argument('-mk', '--max-key', type=int,
                        help='Max. value for key.')
    parser.add_argument('-li', '--min-liveness', type=float,
                        help='Min. value. Detects the presence of an audience in the recording. Higher liveness values represent '
                        'an increased probability that the track was performed live. A value above 0.8 provides strong '
                        'likelihood that the track is live.')
    parser.add_argument('-mli', '--max-liveness', type=float,
                        help='Max. value for liveness.')
    parser.add_argument('-lo', '--min-loudness', type=float,
                        help='Min. value. The overall loudness of a track in decibels (dB). '
                        'Loudness values are averaged across the entire track and are useful for comparing relative '
                        'loudness of tracks. Loudness is the quality of a sound that is the primary psychological '
                        'correlate of physical strength (amplitude). Values typical range between -60 and 0 db.')
    parser.add_argument('-mlo', '--max-loudness', type=float,
                        help='Max. value for loudness.')
    parser.add_argument('-s', '--min-speechiness', type=float,
                        help='Min. value. Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording '
                        '(e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks '
                        'that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain '
                        'both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most '
                        'likely represent music and other non-speech-like tracks.')
    parser.add_argument('-ms', '--max-speechiness', type=float,
                        help='Max. value for speechiness.')
    parser.add_argument('-t', '--min-tempo', type=float,
                        help='Min. value. The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, '
                        'tempo is the speed or pace of a given piece and derives directly from the average beat duration.')
    parser.add_argument('-mt', '--max-tempo', type=float,
                        help='Max. value for tempo.')
    parser.add_argument('-ts', '--min-time_signature', type=int,
                        help='Min. value. An estimated overall time signature of a track. The time signature (meter) is a notational '
                        'convention to specify how many beats are in each bar (or measure).')
    parser.add_argument('-mts', '--max-time_signature', type=int,
                        help='Max. value for time_signature.')
    parser.add_argument('-v', '--min-valence', type=float,
                        help='Min. value. A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. '
                        'Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low '
                        'valence sound more negative (e.g. sad, depressed, angry).')
    parser.add_argument('-mv', '--max-valence', type=float,
                        help='Max. value for valence.')

    return parser.parse_args()

def track_should_be_added(track_audio_features):
    if not track_audio_features:
        return False

    for key, value in FILTERS.items():
        split_filter_key = key.split("_") # e.g. min_tempo.
        try: # Get the actual audio feature value that was received.
            actual_value = track_audio_features[split_filter_key[1]]
        except KeyError:
            return False # TODO: Maybe rather continue?

        if split_filter_key[0] == "min":
            if actual_value < value:
                return False
        elif split_filter_key[0] == "max":
            if actual_value > value:
                return False
    
    return True

def filter_tracks_to_list(to_add, results):
    global FILTERED, SKIPPED

    for track_audio_features in results:
        FILTERED += 1
        if track_should_be_added(track_audio_features):
            print(f"Adding: {track_audio_features['id']}")
            to_add.append(track_audio_features['id'])
        else:
            SKIPPED += 1

def request_audio_features(spotify_client, results):
    to_request = [x['track']['id'] for x in results['items']]
    if to_request:
        return spotify_client.audio_features(tracks=to_request)

    return None

def main():
    global FILTERED, ADDED, SKIPPED

    if not FILTERS:
        raise Exception("No filters specified.")

    authorization = SpotifyOAuth(
        scope=PERMISSIONS_SCOPE,
        client_id=user_secrets.CLIENT_ID,
        client_secret=user_secrets.CLIENT_SECRET,
        redirect_uri=user_secrets.REDIRECT_URI,
        open_browser=False
    )
    spotify_client = spotipy.Spotify(auth_manager=authorization)
    if not spotify_client.me():
        raise Exception("Failed to authorize app client or user.")

    print(f"Authorized as: {spotify_client.me()['display_name']}")

    used_flags = "".join(f"{filter}:{value}, " for filter, value in FILTERS.items())
    print(f"Using audio feature flags: {used_flags[:-2]}")

    created_playlist = spotify_client.user_playlist_create(
        user=spotify_client.me()['id'],
        name=f"My filtered playlist",
        description="Automatically generated with https://github.com/fuzzysearch404/SpotifyPlaylistScripts"
        f" | Used flags: {used_flags[:-2]}."
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

    filter_tracks_to_list(to_add, request_audio_features(spotify_client, results))
    while results['next']:
        results = spotify_client.next(results)
        filter_tracks_to_list(to_add, request_audio_features(spotify_client, results))

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
    # Remove args where value is None.
    FILTERS = dict([x for x in args.__dict__.items() if x[1] is not None])
    
    main()