import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

class Library:
    def __init__(self, spotify_client_id="90b9bbdd175d418bbdd1e0a9dda6991c", spotify_client_secret='af4e3f49c1174efbbc0c615685e6fc09'):
    # TODO: move credentials to env file
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        os.environ["SPOTIPY_CLIENT_ID"] = self.spotify_client_id
        os.environ["SPOTIPY_CLIENT_SECRET"] = self.spotify_client_secret
        # initialize spotify client
        self.spotify_client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.library = {}
        self.artist_nameuri_mapping = {}
        self.artist_uriname_mapping = {}
        self.album_nameuri_mapping = {}
        self.album_uriname_mapping = {}
        self.track_nameuri_mapping = {}
        self.track_uriname_mapping = {}
        self.collections = {}

    def add_artist(self, search_name, save_cache=True):
        # initialize spotify client
        results = self.spotify_client.search(q='artist:' + search_name, type='artist')
        ARTISTS = {}
        if results.get('artists').get('items'):
            artist_name = results.get('artists').get('items')[0].get('name')
        else:
            return ARTISTS
        ARTISTS[artist_name] = {}
        ARTISTS[artist_name]['uri'] = results.get('artists').get('items')[0].get('uri')
        albums = self.spotify_client.artist_albums(ARTISTS[artist_name]['uri']).get('items')
        ARTISTS[artist_name]['albums'] = {i.get('name'):{'uri':i.get('uri')} for i in albums}
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
        self.artist_nameuri_mapping = {artist: self.library[artist].get('uri') for artist in self.library}
        self.artist_uriname_mapping = {v:k for (k,v) in self.artist_nameuri_mapping.items()}
        album_nameuri_mapping = {}
        track_nameuri_mapping = {}
        for artist in self.library:
            albums = self.library[artist].get('albums')
            for album_name in albums:
                album_nameuri_mapping[album_name] = self.library[artist].get('albums').get(album_name).get('uri')
                tracks = self.library[artist].get('albums').get(album_name).get('tracks')
                for track in tracks:
                    track_nameuri_mapping[track] = self.library[artist].get('albums').get(album_name).get('tracks').get(track).get('uri')
        self.album_nameuri_mapping = album_nameuri_mapping
        self.track_nameuri_mapping = track_nameuri_mapping
        self.album_uriname_mapping = {v:k for (k, v) in album_nameuri_mapping.items()}
        self.track_uriname_mapping = {v:k for (k, v) in track_nameuri_mapping.items()}

    def update_collections(self):
        # TODO add cache to YAML file
        self.collections = {(self.library.get(art).get('uri'), 'artist'): {
            (self.library.get(art).get('albums').get(al).get('uri'), 'album'): [
                (self.library.get(art).get('albums').get(al).get('tracks').get(tr).get('uri'), 'track') for tr
                in self.library.get(art).get('albums').get(al).get('tracks')] for al in
            self.library.get(art).get('albums')} for art in self.library}
        return self.collections



# test
#lib = Library()
#print(lib.add_artist('Parcels'))
















