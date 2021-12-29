import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import os

scope = "user-library-read"
SPOTIFY_CLIENT = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
SPOTIFY_CLIENT = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))




#for key in pathuri_mapping:
#    uri = pathuri_mapping[key]
def get_audio_features(uri, spotify_client, folder):
    audio_feature = spotify_client.audio_analysis(uri)
    with open("/home/pi/pythonproject/raspberrypi_sensehat_music/playlist_utils/cache_jsons/audio_features/{}.json".format(uri),'w') as file:
        json.dump(audio_feature, file)