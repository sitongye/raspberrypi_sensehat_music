import os
import subprocess as sp
import wave
import numpy as np
import pygame
from pygame.locals import *
from scipy.fftpack import dct
from sense_hat import SenseHat

x_axis_color_dict_parcels = {6:tuple((218, 217, 218)),
                             7:tuple((218, 217, 218)),
                             0:tuple((42, 75, 114)),
                             1:tuple((42, 75, 114)),
                             2:tuple((114, 85, 62)),
                             3:tuple((114, 85, 62)),
                             4:tuple((133, 152, 172)),
                             5:tuple((133, 152, 172))}


class OneSong:
    def __init__(self, music_path, sensehat, album=None, song_art=None, volume=1,display_size=8):
        '''

        :param music_path: str. absolute path to music file
        :param sensehat: initialised sensehat object
        :param album: Album Class Obejct
        :param song_art: PixelArt Class Object
        :param volume: int. 1 by default
        '''
        self.sensehat = sensehat
        self.music_path = music_path
        # TODO: hold out to external configuration
        self.display_size = display_size
        self.album = album
        self.song_art = song_art
        self.volume = volume
        head_tail = os.path.split(self.music_path)
        self.file_name = head_tail[1]
        filename_raw, extension = os.path.splitext(self.file_name)
        # check if the file is in wav form
        if extension != "wav":
            try:
                fnull = open(os.devnull, "w")
                pieq_tmp = os.path.expanduser("~") + "/.pieq_tmp/"
                wav_path = pieq_tmp + filename_raw + ".wav"
                if not os.path.isfile(wav_path):
                    print("Decompressing...")
                    sp.call(["mkdir", "-p", pieq_tmp])
                    sp.call(["ffmpeg", "-i", self.music_path, wav_path], stdout=fnull, stderr=sp.STDOUT)
                self.wav_path = wav_path
                tmp_file_created = True
            except FileExistsError:
                print('failed to convert to wav file')
        else:
            self.wav_path = self.music_path
        self.status = 'stopped'
        self.feature_dict = self.get_features()
        self.nframes = self.feature_dict.get('nframes') # dynamically changes
        #TODO: hold out to external configuration
        self.FPS = 10
        pygame.mixer.init()
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

    def play(self):
        pygame.mixer.music.load(self.wav_path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()
        start_time = 0.0
        pygame.time.Clock().tick()
        self.status = 'playing'

    def _visualizer(self, bgd_clr=(0, 0, 0), fill_clr=(255, 255, 255), x_color_dict=None):
        nums = int(self.nframes)
        h = abs(dct(self.feature_dict.get('wave_data')[0][self.feature_dict['nframes'] - nums:self.feature_dict['nframes']  - nums + self.display_size], 2))
        h = [min(self.display_size, int(i ** (1 / 2.5) * self.display_size / 100) + 1) for i in h]
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
        self.play()
        while True:
            if self.nframes <= 0:
                self.status = "stopped"
                self.sensehat.clear()
            self.fpsclock.tick(self.FPS)
            self.vis()
            
##test
sense = SenseHat()
testsong = OneSong('/home/pi/Music/Lightenup.mp3', sense, album=None, song_art=None, volume=1,display_size=8)
testsong.run()