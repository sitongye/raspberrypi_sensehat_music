import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
import json
from dotenv import load_dotenv

try:
    load_dotenv('.env')
except:
    print('failed to load env file, skipping')


def save_as_cache(dct, outputpath):
    with open(outputpath, 'w') as outfile:
        json.dump(dct, outfile)


class Library:
    def __init__(self, config="../config.json"):
        # initialize spotify client
        with open(config) as file:
            self.CONFIG = json.load(file)
        if not os.path.isdir(os.path.join(self.CONFIG.get("PROJECT_BASE_PATH"), "Library")):
            os.mkdir(os.path.join(self.CONFIG.get("PROJECT_BASE_PATH"), "Library"))
        self.library_path = os.path.join(self.CONFIG.get("PROJECT_BASE_PATH"), "Library")
        if not os.path.isdir(os.path.join(self.library_path, "Meta")):
            os.mkdir(os.path.join(self.library_path, "Meta"))
        self.spotify_client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.spotify_client2 = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))
        if os.path.exists(os.path.join(self.library_path, "Meta", "library.json")):
           with open(os.path.join(self.library_path, "Meta", "library.json")) as f:
               self.library = json.load(f)
        else:
            self.library = {}
        if os.path.exists(os.path.join(self.library_path, "Meta", "artist_nameuri_mapping.json")):
           with open(os.path.join(self.library_path, "Meta", "artist_nameuri_mapping.json")) as f:
               self.library = json.load(f)
        else:
            self.artist_nameuri_mapping = {}
        self.artist_uriname_mapping = {}
        if os.path.exists(os.path.join(self.library_path, "Meta", "album_nameuri_mapping.json")):
           with open(os.path.join(self.library_path, "Meta", "album_nameuri_mapping.json")) as f:
               self.album_nameuri_mapping = json.load(f)
        else:
            self.album_nameuri_mapping = {}
        self.album_uriname_mapping = {}
        if os.path.exists(os.path.join(self.library_path, "Meta", "album_nameuri_mapping.json")):
           with open(os.path.join(self.library_path, "Meta", "album_nameuri_mapping.json")) as f:
               self.album_nameuri_mapping = json.load(f)
        else:
            self.album_nameuri_mapping = {}
        if os.path.exists(os.path.join(self.library_path, "Meta", "track_nameuri_mapping.json")):
           with open(os.path.join(self.library_path, "Meta", "track_nameuri_mapping.json")) as f:
               self.track_nameuri_mapping = json.load(f)
        else:
            self.track_nameuri_mapping = {}
        self.track_uriname_mapping = {}
        self.collections = {}
        self.pathuri_mapping = {}

    def add_artist(self, search_name, save_cache=True):
        if search_name in self.artist_nameuri_mapping:
            print("artist already in library")
            return None
        # if artist not yet in the library, search using spotify api
        # initialize spotify client
        try:
            print("using spotify crendentials")
            results = self.spotify_client.search(q='artist:' + search_name, type='artist')
        except:
            print("using spotify authentication")

        ARTISTS = {}
        if results.get('artists').get('items'):
            artist_name = results.get('artists').get('items')[0].get('name')
            if artist_name in self.library:
                return None
        else:
            return ARTISTS
        ARTISTS[artist_name] = {}
        ARTISTS[artist_name]['uri'] = results.get('artists').get('items')[0].get('uri')
        albums = self.spotify_client.artist_albums(ARTISTS[artist_name]['uri']).get('items')
        ARTISTS[artist_name]['albums'] = {i.get('name'): {'uri': i.get('uri')} for i in albums}
        for album_name in ARTISTS[artist_name]['albums']:
            album_uri = ARTISTS[artist_name]['albums'][album_name].get('uri')
            tracks = self.spotify_client.album_tracks(album_uri).get('items')
            ARTISTS[artist_name]['albums'][album_name]['tracks'] = {
                i.get('name'): {'track_number': i.get('track_number'),
                                'disc_number': i.get('disc_number'),
                                'duration_ms': i.get('duration_ms'),
                                'uri': i.get('uri'),
                                } for i in tracks}
        self.library[artist_name] = ARTISTS.get(artist_name)
        return ARTISTS

    def update_mapping(self):
        '''
        :param type: {'artist', 'album', 'track')
        :param mode: {'fromuri', 'fromname'}
        :return: dict
        '''
        self.artist_nameuri_mapping.update({artist: self.library[artist].get('uri') for artist in self.library})
        self.artist_uriname_mapping = {v: k for (k, v) in self.artist_nameuri_mapping.items()}
        for artist in self.library:
            albums = self.library[artist].get('albums')
            for album_name in albums:
                if album_name not in self.artist_nameuri_mapping:
                    self.album_nameuri_mapping[album_name] = self.library[artist].get('albums').get(album_name).get('uri')
                tracks = self.library[artist].get('albums').get(album_name).get('tracks')
                for track in tracks:
                    if track not in self.track_nameuri_mapping:
                        self.track_nameuri_mapping[track] = self.library[artist].get('albums').get(album_name).get('tracks').get(
                            track).get('uri')
        self.album_uriname_mapping = {v: k for (k, v) in self.album_nameuri_mapping.items()}
        self.track_uriname_mapping = {v: k for (k, v) in self.track_nameuri_mapping.items()}

    def update_collections(self):
        # TODO add cache to YAML file
        self.collections = {self.library.get(art).get('uri'): {
            self.library.get(art).get('albums').get(al).get('uri'): [
                self.library.get(art).get('albums').get(al).get('tracks').get(tr).get('uri') for tr
                in self.library.get(art).get('albums').get(al).get('tracks')] for al in
            self.library.get(art).get('albums')} for art in self.library}
        return self.collections

    def _get_audiofeatures(self, track_id):
        try:
            return self.spotify_client.audio_analysis(track_id)
        except:
            return self.spotify_client2.audio_analysis(track_id)

    def get_trackpath_uri_mapping(self, basemusicpath=r'/home/pi/pythonproject/raspberrypi_sensehat_music/Music/'):
        if self.track_nameuri_mapping is None:
            self.update_mapping()
        music_files = []
        for root, dirs, files in os.walk(basemusicpath):
            for file in files:
                music_files.append(os.path.join(root, file))
        path_uri = {os.path.split(song_path)[1]: self.track_nameuri_mapping.get(
            os.path.split(song_path)[1].split('.')[-2].strip(), None) for song_path in music_files}
        self.pathuri_mapping = path_uri
        return path_uri


# test
parcels = Library()
parcels.add_artist('Parcels')
parcels.update_mapping()
parcels.update_collections()
parcels.get_trackpath_uri_mapping()

# save_as_cache(parcels.library, 'library.json')
# save_as_cache(parcels.artist_nameuri_mapping,'artist_nameuri_mapping.json')
# save_as_cache(parcels.artist_uriname_mapping,'artist_uriname_mapping.json')
# save_as_cache(parcels.album_nameuri_mapping, 'album_nameuri_mapping.json')
# save_as_cache(parcels.album_uriname_mapping, 'album_uriname_mapping.json')
# save_as_cache(parcels.track_nameuri_mapping, 'track_nameuri_mapping.json')
# save_as_cache(parcels.track_uriname_mapping, 'track_uriname_mapping.json')
# save_as_cache(parcels.collections, 'collections.json')














