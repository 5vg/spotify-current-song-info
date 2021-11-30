import json

import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
import urllib.request

def key_setup(filename):
    with open(filename, 'r') as f:
        data = f.read().split('\n', 1)
        return data[0], data[1]

def get_spotify_code(uri):
    # format :
    # https://scannables.scdn.co/uri/plain/[format]/[background-color-in-hex]/[code-color-in-text]/[size]/[spotify-URI]

    final_url = 'https://scannables.scdn.co/uri/plain/png/000000/white/640/' + uri

    return final_url


def parser(raw_results):
    filtered_results = {
        'is_playing': raw_results['is_playing'],
        'progress': raw_results['progress_ms'],
        'duration': raw_results['item']['duration_ms'],
        'name': raw_results['item']['name'],
        'artist_name': raw_results['item']['artists'][0]['name'],
        'album_name': raw_results['item']['album']['name'],
        'spotify_code': get_spotify_code(raw_results['item']['uri']),
        'cover_url': raw_results['item']['album']['images'][0]['url']
    }
    return filtered_results


def get_new_results(sp):
    raw_results = sp.currently_playing()
    filterSuccess = False
    filtered_results = {}
    try:
        filtered_results.update(parser(raw_results))
        filterSuccess = True
        return_packet = (filtered_results, filterSuccess)
        return return_packet
    except TypeError:
        return_packet = (filtered_results, filterSuccess)
        return return_packet


if __name__ == '__main__':

    key_file = "keys.txt"
    client_id, client_secret = key_setup(key_file)

    scope = 'user-read-currently-playing'

    spotify_connection = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                                                   client_id=client_id,
                                                                   client_secret=client_secret,
                                                                   redirect_uri='http://localhost:8080'))

    results = get_new_results(spotify_connection)
    checked_time = int(round(time.time() * 1000))
    prev_song = ''

    while True:
        cur_time = int(round(time.time() * 1000))

        if cur_time - checked_time >= 500:
            results = get_new_results(spotify_connection)
            checked_time = cur_time

        if results[1] and results[0]['is_playing']:
            cur_song = results[0]['name']
            if cur_song != prev_song:
                with open('song-name.txt', 'w') as f1:
                    f1.write(results[0]['name'])
                with open('artist-name.txt', 'w') as f2:
                    f2.write(results[0]['artist_name'])
                with open('album-name.txt', 'w') as f3:
                    f3.write(results[0]['album_name'])
                urllib.request.urlretrieve(results[0]['spotify_code'], 'spotify-code.jpg')
                urllib.request.urlretrieve(results[0]['cover_url'], 'cover-url.jpg')
            prev_song = cur_song
