# Spoti2Saber

Creates Beat Saber playlist from Spotify library using BeatSaver maps

## Requirements:

`pip install argparse requests`

## Usage:

You need to get Spotify OAUTH token here: https://developer.spotify.com/console/get-current-user-saved-tracks

`python3 spoti2saber.py [-h] [--limit LIMIT] playlist_name oauth_token`

## Help

```
usage: spoti2saber.py [-h] [--limit LIMIT] playlist_name oauth_token

positional arguments:
  playlist_name  Playlist name
  oauth_token    Spotify OAUTH token

optional arguments:
  -h, --help     show this help message and exit
  --limit LIMIT  Max number of "similar" songs (Default: 3). 
                 May flood your playlist with unrelated songs if set too high
```