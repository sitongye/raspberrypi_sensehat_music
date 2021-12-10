import os
import subprocess as sp
import wave
import numpy as np
import pygame
from pygame.locals import *
from scipy.fftpack import dct
from sense_hat import SenseHat



def formatwave(music_path):
    head_tail = os.path.split(music_path)
    file_name = head_tail[1]
    filename_raw, extension = os.path.splitext(file_name)
        # check if the file is in wav form
    if extension != "wav":
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
    return wav_path
    
    
x_axis_color_dict_parcels = {6:tuple((218, 217, 218)),
                             7:tuple((218, 217, 218)),
                             0:tuple((42, 75, 114)),
                             1:tuple((42, 75, 114)),
                             2:tuple((114, 85, 62)),
                             3:tuple((114, 85, 62)),
                             4:tuple((133, 152, 172)),
                             5:tuple((133, 152, 172))}


class Player:
    def __init__(self, music_basepath, sensehat, album=None, song_art=None, volume=1,display_size=8, viz_clr=None):
        '''

        :param music_path: str. absolute path to music file
        :param sensehat: initialised sensehat object
        :param album: Album Class Obejct
        :param song_art: PixelArt Class Object
        :param volume: int. 1 by default
        '''
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
        self.wav_path = formatwave(self.music_path)
        # TODO: hold out to external configuration
            
        self.display_size = display_size
        self.album = album
        self.song_art = song_art
        self.volume = volume
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
        while True:
            self.play()
            if self.nframes <= 0:
                self.status = "stopped"
                self.sensehat.clear()
            while pygame.mixer.music.get_busy():
                self.fpsclock.tick(self.FPS)
                self.vis()
                for x in self.sensehat.stick.get_events():
                    if x.direction == 'right':
                        self.idx_currenttrack = self.idx_currenttrack + 1
                        if self.idx_currenttrack >= self.nr_tracks:
                            self.idx_currenttrack = 0
                        pygame.mixer.music.stop()
                        self.sensehat.clear()
                        self.music_path = self.music_files[self.idx_currenttrack]
                        self.wav_path = formatwave(self.music_path)
                        self.feature_dict = self.get_features()
                        self.nframes = self.feature_dict.get('nframes')
                        self.play()
                        start_time = 0.0
                    if x.direction == 'left':
                        self.idx_currenttrack = self.idx_currenttrack - 1
                        if self.idx_currenttrack < 0:
                            self.idx_currenttrack = 0
                        pygame.mixer.music.stop()
                        self.sensehat.clear()
                        self.music_path = self.music_files[self.idx_currenttrack]
                        self.wav_path = formatwave(self.music_path)
                        self.feature_dict = self.get_features()
                        self.nframes = self.feature_dict.get('nframes')
                        self.play()
                    if x.direction == 'up':
                        self.volume = self.volume + 0.05
                        if self.volume >- 1.0:
                            self.volume = 1.0
                        pygame.mixer.music.set_volume(self.volume)
                    if x.direction == 'down':
                        self.volume = self.volume - 0.05
                    if self.volume < 0.0:
                        self.volume = 0.0
                    pygame.mixer.music.set_volume(self.volume)
##test
sense = SenseHat()

testplayer = Player('/home/pi/pythonproject/raspberrypi_sensehat_music/music', sense, album=None, song_art=None, volume=1,display_size=8, viz_clr=x_axis_color_dict_parcels)
testplayer.run()
