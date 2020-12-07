Custom Spotify playlist Python scripts for my personal uses.

## Requirements
https://github.com/plamere/spotipy
```
pip install spotipy
```

## Setup
Create new Spotify web application at https://developer.spotify.com. 
Create `secrets.py` python file as per example `secrets_example.py`.

## Custom playlist scripts
#### Liked songs by album release years:
`liked_by_album_released_years.py` - Generates a playlist from your liked songs
of songs that are released in specific years. For example:
songs that have been released in a time period between 2005 and 2018.
**Arguments:**  
`-s` or `--start-year` - Starting year for liked songs to filter.  
`-e` or `--end-year` - Ending year for liked songs to filter.  
