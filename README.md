Custom Spotify playlist Python scripts for my personal uses.

## Requirements
https://github.com/plamere/spotipy
```
pip install spotipy
```

## Setup
Create a new Spotify web application at https://developer.spotify.com. 
Create a `secrets.py` Python file as per example `secrets_example.py`.

## Custom playlist scripts
### Liked songs by album release years:
`liked_by_album_released_years.py` - Generates a playlist from your liked songs, 
of songs that are released in specific years. For example:
songs that have been released in a time period between 2005 and 2018.  
**Arguments:**  
`-s` or `--start-year` - Starting release year for liked songs to filter. Required.  
`-e` or `--end-year` - Ending release year for liked songs to filter. Required.  
### Liked songs by audio features:
`liked_by_audio_features.py` - Generates a playlist from your liked songs,
of songs that meet criteria by audio feature filters you set. For example:
songs that are above tempo 120 BPM, below 200 BPM and valance is above 0.65.  
**Available filter flags (Using atleast one is mandatory):**  
`-a` or `--min-acousticness` - Min. value for acousticness. (float 0.0 - 1.0)  
`-ma` or `--max-acousticness` - Max. value for acousticness. (float 0.0 - 1.0)  
`-d` or `--min-danceability` - Min. value for danceability. (float 0.0 - 1.0)  
`-md` or `--max-danceability` - Max. value for danceability. (float 0.0 - 1.0)  
`-du` or `--min-duration_ms` - Min. value for duration_ms. (int)  
`-mdu` or `--max-duration_ms` - Max. value for duration_ms. (int)  
`-e` or `--min-energy` - Min. value for energy. (float 0.0 - 1.0)  
`-me` or `--max-energy` - Max. value for energy. (float 0.0 - 1.0)  
`-i` or `--min-instrumentalness` - Min. value for instrumentalness. (float 0.0 - 1.0)  
`-mi` or `--max-instrumentalness` - Max. value for instrumentalness. (float 0.0 - 1.0)  
`-k` or `--min-key` - Min. value for key. (int)  
`-mk` or `--max-key` - Max. value for key. (int)  
`-li` or `--min-liveness` - Min. value for liveness. (float 0.0 - 1.0)  
`-mli` or `--max-liveness` - Max. value for liveness. (float 0.0 - 1.0)  
`-lo` or `--min-loudness` - Min. value for loudness. (float)  
`-mlo` or `--max-loudness` - Max. value for loudness. (float)  
`-s` or `--min-speechiness` - Min. value for speechiness. (float 0.0 - 1.0)  
`-ms` or `--max-speechiness` - Max. value for speechiness. (float 0.0 - 1.0)  
`-t` or `--min-tempo` - Min. value for tempo. (float)  
`-mt` or `--max-tempo` - Max. value for tempo. (float)  
`-ts` or `--min-time_signature` - Min. value for time_signature. (int)  
`-mts` or `--max-time_signature` - Max. value for time_signature. (int)  
`-v` or `--min-valence` - Min. value for valance. (float 0.0 - 1.0)  
`-mv` or `--max-valence` - Max. value for valance. (float 0.0 - 1.0)  
**For detailed parameter descriptions use `-h` or `--help` flag, or visit official Spotify API reference:  
https://developer.spotify.com/documentation/web-api/reference/tracks/get-several-audio-features/**  