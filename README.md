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
#### Liked songs by album release years:
`liked_by_album_released_years.py` - Generates a playlist from your liked songs, 
of songs that are released in specific years. For example:
songs that have been released in a time period between 2005 and 2018.  
**Arguments:**  
`-s` or `--start-year` - Starting release year for liked songs to filter. Required.  
`-e` or `--end-year` - Ending release year for liked songs to filter. Required.  
