import os
import subprocess as sp
import wave
import numpy as np
import pygame
import time
from time import sleep
from pygame.locals import *
from scipy.fftpack import dct
from sense_emu import SenseHat
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
#from metronome.metronome import metronome
from dotenv import load_dotenv
import json

load_dotenv('.env')
SPOTIFY_CLIENT = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

background = (0,0,0)
R = (198, 30, 74)       #raspberrytips red
W = (255, 255, 255)
        
def formatwave(music_path):
    head_tail = os.path.split(music_path)
    file_name = head_tail[1]
    filename_raw, extension = os.path.splitext(file_name)
        # check if the file is in wav form
    if extension != ".wav":
        try:
            fnull = open(os.devnull, "w")
            pieq_tmp = os.path.expanduser("~") + "/.pieq_tmp/"
            wav_path = pieq_tmp + filename_raw + ".wav"
            if not os.path.isfile(wav_path):
                print("Decompressing...")
                sp.call(["mkdir", "-p", pieq_tmp])
                sp.call(["ffmpeg", "-i", music_path, wav_path], stdout=fnull, stderr=sp.STDOUT)
        except FileExistsError:
            print('failed to convert to wav file')
    else:
        wav_path = music_path
    file_name = '.'.join(file_name.split('.')[:-1])
    return wav_path, file_name
    
    
x_axis_color_dict_parcels = {6:tuple((218, 217, 218)),
                             7:tuple((218, 217, 218)),
                             0:tuple((42, 75, 114)),
                             1:tuple((42, 75, 114)),
                             2:tuple((114, 85, 62)),
                             3:tuple((114, 85, 62)),
                             4:tuple((133, 152, 172)),
                             5:tuple((133, 152, 172))}


def wait(delay):
    end_time = time.time() + delay
    while end_time > time.time():
        continue

class Player:
    def __init__(self, music_basepath, sensehat, volume=1,display_size=8, viz_clr=None):
        '''

        :param music_path: str. absolute path to music file
        :param sensehat: initialised sensehat object
        :param song_art: PixelArt Class Object
        :param volume: int. 1 by default
        '''
        # load mapping
        with open(os.path.join('.','playlist_utils','cache_jsons','pathuri_mapping.json')) as file:
            pathuri_mapping = json.load(file, encoding='utf8')
        self.sensehat = sensehat
        self.viz_clr = viz_clr
        self.music_basepath = music_basepath #folder
        self.music_files = []
        for root, dirs, files in os.walk(self.music_basepath):
            for file in files:
                self.music_files.append(os.path.join(root,file))
        self.music_files.sort()
        self.nr_tracks = len(self.music_files)
        self.idx_currenttrack = 0
        self.music_path = self.music_files[self.idx_currenttrack]
        self.wav_path, self.file_name = formatwave(self.music_path)
        self.track_uri = pathuri_mapping.get(self.file_name+'.wav',None)
        print('filename', self.file_name+'.wav')
        print('track_uri',self.track_uri)
        if self.track_uri is not None:
            self.audio_features = SPOTIFY_CLIENT.audio_analysis(self.track_uri)
        else:
            self.audio_features = {}
        print(self.audio_features)
        
        # TODO: hold out to external configuration
        self.display_size = display_size
        self.volume = volume
        self.status = 'stopped'
        self.feature_dict = self.get_features()
        self.nframes = self.feature_dict.get('nframes') # dynamically changes
        #TODO: hold out to external configuration
        self.FPS = 10
        pygame.mixer.init(44100, -16, 2, 64)
        pygame.mixer.set_num_channels(5)
        self.fpsclock = pygame.time.Clock()

    def get_features(self):
        feature_dict = {}
        f = wave.open(self.wav_path, 'rb')
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        feature_dict['nchannels'] = nchannels
        feature_dict['sampwidth'] = sampwidth
        feature_dict['framerate'] = framerate
        feature_dict['nframes'] = nframes
        str_data = f.readframes(nframes)
        f.close()
        wave_data = np.frombuffer(str_data, dtype=np.short)
        wave_data.shape = -1, 2
        feature_dict['wave_data'] = wave_data.T
        #num = nframes
        return feature_dict

    def _get_time(self):
        seconds = max(0, pygame.mixer.music.get_pos() / 1000)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        hms = ("%02d:%02d:%02d" % (h, m, s))
        return hms

    def play(self, metronome_on=False):
        pygame.mixer.music.stop()
        self.sensehat.clear()
        self.music_path = self.music_files[self.idx_currenttrack]
        self.wav_path, self.file_name = formatwave(self.music_path)
        self.feature_dict = self.get_features()
        self.nframes = self.feature_dict.get('nframes')
        self.sensehat.show_message("Now Playing: {}".format(self.file_name), 0.05, W, background)
        pygame.mixer.music.load(self.wav_path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()
        start_time = 0.0
        self.status = 'playing'
        if metronome_on:
            if self.audio_features:
                bpm = round(self.audio_features.get('track').get('tempo'))
                print(float(bpm), "bpm")
                delay = 60/bpm
                count = 0
                beat = 0
                mode = 4
                multiple = 8
                eo_fadein = self.audio_features.get('track').get('end_of_fade_in')
                if eo_fadein!= 0:
                    wait(eo_fadein)
                while not self.sensehat.stick.get_events()[-1].direction!='middle':
                # increment count after every wait and beat after ever 4 counts
                    count += 1
                    if count > mode:
                        count = 1
                        beat += 1
                    # set metronome audio according to beat count
                    #wave_obj = simpleaudio.WaveObject.from_wave_file('./metronome/metronome.wav')
                    metronome_sound = pygame.mixer.Sound('./metronome/metronome.wav')
                    pygame.mixer.find_channel(True).play(metronome_sound)
                    if count == 1:
                        metronome_up = pygame.mixer.Sound('./metronome/metronomeup.wav')
                        pygame.mixer.find_channel(True).play(metronome_up)
                    wait(delay-0.01)
            
            
    def play_metronome(self):
        pygame.mixer.music.stop()
        self.sensehat.clear()
        self.music_path, self.file_name = formatwave(self.music_path)


    def _visualizer(self, bgd_clr=(0, 0, 0), fill_clr=(255, 255, 255), x_color_dict=None):
        sleep(0.08)
        nums = int(self.nframes)
        h = abs(dct(self.feature_dict.get('wave_data')[0][self.feature_dict['nframes'] - nums:self.feature_dict['nframes']  - nums + self.display_size], 2))
        h = [min(self.display_size, int(i ** (1 / 2.5) * self.display_size / 100) + 1) for i in h]
        if self.viz_clr:
            x_color_dict = self.viz_clr
        self._draw_bars_pixels(h, bgd_clr=bgd_clr, fill_clr=fill_clr, x_color_dict=x_color_dict)

    def _draw_bars_pixels(self, h, bgd_clr=(0, 0, 0), fill_clr=(255, 255, 255), x_color_dict=None):
        matrix = [bgd_clr] * 64
        np_matrix = np.array(matrix).reshape(8, 8, 3)
        for i in range(len(h)):
            if x_color_dict is not None:
                fill_clr = x_color_dict[i]
            np_matrix[i][(8 - h[i]):] = fill_clr
        # update column by column
        for X in range(0, 8):
            for Y in range(0, 8):
                self.sensehat.set_pixel(X, Y, np_matrix[X][Y])

    def vis(self):
        if self.status == "stopped":
            num = self.feature_dict.get('nframes')
            return
        elif self.status == "paused":
            self._visualizer()
        else:
            self.nframes -= self.feature_dict['framerate'] / self.FPS
            if self.nframes > 0:
                self._visualizer()


    def run(self):
        '''
        play music and visualise
        :return:
        '''
        curr_time = time.localtime()
        curr_clock = time.strftime("%H:%M:%S", curr_time)
        # greeting
        if int(curr_clock.split(':')[0])<=12:
            greeting = 'Guten Morgen'
        elif int(curr_clock.split(':')[0])<17:
            
            greeting = "Guten Nachmittag"
        else:
            greeting = 'Guten Abend'
        # print greeting
        self.sensehat.clear()
        self.sensehat.show_message("{}, Martin :)".format(greeting), 0.05, W, background)
        
        while True:
            #self.sensehat.clear()
            self.play()
            while pygame.mixer.music.get_busy():
                self.fpsclock.tick(self.FPS)
                self.vis()
                if self.nframes <= 0:
                    self.status = "stopped"
                    self.idx_currenttrack = self.idx_currenttrack + 1
                    if self.idx_currenttrack >= self.nr_tracks:
                        self.idx_currenttrack = 0
                x,y,z = self.sensehat.get_accelerometer_raw().values()
                x = abs(x)
                y = abs(y)
                z = abs(z)
                if x>2 or y>2 or z>2:
                    self.idx_currenttrack = random.choice(range(self.nr_tracks))
                    print('play ',self.file_name)
                    self.play()
                for x in self.sensehat.stick.get_events():
                    # turn on metronome
                    #if x.direction == 'right' and x.action == 'pressed':
                    if x.direction == 'right' and x.action == 'pressed':
                        self.idx_currenttrack = self.idx_currenttrack + 1
                        if self.idx_currenttrack >= self.nr_tracks:
                            self.idx_currenttrack = 0
                        print('play ',self.file_name)
                        self.play()
                        start_time = 0.0
                    if x.direction == 'left' and x.action == 'pressed':
                        self.idx_currenttrack = self.idx_currenttrack - 1
                        if self.idx_currenttrack < 0:
                            self.idx_currenttrack = 0
                        pygame.mixer.music.stop()
                        #self.sensehat.clear()
                        print('play ',self.file_name)
                        self.play()
                    if x.direction == 'up' and x.action == 'pressed':
                        self.volume = self.volume + 0.05
                        if self.volume >- 1.0:
                            self.volume = 1.0
                        pygame.mixer.music.set_volume(self.volume)
                    if x.direction == 'down' and x.action == 'pressed':
                        self.volume = self.volume - 0.05
                        if self.volume < 0.0:
                            self.volume = 0.0
                        pygame.mixer.music.set_volume(self.volume)
##test
sense = SenseHat()

testplayer = Player('/home/pi/pythonproject/raspberrypi_sensehat_music/Music', sense, volume=1,display_size=8, viz_clr=x_axis_color_dict_parcels)
testplayer.run()
