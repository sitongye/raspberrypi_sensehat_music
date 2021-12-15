import os
import subprocess as sp
import wave
import numpy as np
import pygame
import time
from time import sleep
from pygame.locals import *
from scipy.fftpack import dct
from sense_hat import SenseHat
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import wave
from dotenv import load_dotenv
import json
import simpleaudio

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

load_dotenv('.env')
SPOTIFY_CLIENT = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

x_axis_color_dict_parcels = {6:tuple((218, 217, 218)),
                             7:tuple((218, 217, 218)),
                             0:tuple((42, 75, 114)),
                             1:tuple((42, 75, 114)),
                             2:tuple((114, 85, 62)),
                             3:tuple((114, 85, 62)),
                             4:tuple((133, 152, 172)),
                             5:tuple((133, 152, 172))}
with open(os.path.join('.','playlist_utils','cache_jsons','pathuri_mapping.json')) as file:
	pathuri_mapping = json.load(file, encoding='utf8')

music_path = '/home/pi/pythonproject/raspberrypi_sensehat_music/Music/Day_Night/2. Free.wav'
wav_path, file_name = formatwave(music_path)
track_uri = pathuri_mapping.get(file_name+'.wav',None)
print('filename', file_name+'.wav')
print('track_uri',track_uri)
if track_uri is not None:
	audio_features = SPOTIFY_CLIENT.audio_analysis(track_uri)
else:
    audio_features = {}
with open('tmp_features.json', 'w') as file:
	json.dump(audio_features,file)

background = (0,0,0)
R = (198, 30, 74)       #raspberrytips red
W = (255, 255, 255)

def wait(delay):
    end_time = time.time() + delay
    while end_time > time.time():
        continue



def get_features(wav_path):
    feature_dict = {}
    f = wave.open(wav_path, 'rb')
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
    return feature_dict


def play_metronome(wav_path):
    volume=0.3
    sensehat.clear()
    feature_dict = get_features(wav_path)
    nframes = feature_dict.get('nframes')
    track_uri = pathuri_mapping.get(file_name+'.wav',None)
    if track_uri is not None:
        audio_features = SPOTIFY_CLIENT.audio_analysis(track_uri)
    else:
        audio_features = {}
    if audio_features:
        bpm = round(audio_features.get('track').get('tempo'))
        metronome_on = True
        print(float(bpm), "bpm")
        delay = 60.0/float(bpm)
        count = 0
        beat = 0
        mode = 4
        multiple = 8
        eo_fadein = audio_features.get('track').get('end_of_fade_in')
    else:
        eo_fadein = 0.0
    pygame.mixer.init(frequency=feature_dict['framerate'], buffer=64)
    pygame.mixer.set_num_channels(5)
    pygame.mixer.music.load(wav_path)
    pygame.mixer.music.set_volume(0.1)
    sensehat.show_message("Playing: {}".format(file_name), 0.05, W, background)
    pygame.mixer.music.play()
    status = 'playing'
    start_time = 0.0
    if eo_fadein!= 0.0:
    #    print('fade in',eo_fadein)
        wait(audio_features.get('beats')[0].get('start'))
    else:
        wait(0.001)
    #metronome_sound = pygame.mixer.Sound('./metronome/metronome.wav')
    #metronome_up = pygame.mixer.Sound('./metronome/metronomeup.wav')
    while metronome_on:
        start = time.time()
        events = sensehat.stick.get_events()
        #if len(events)!=0 and events[-1].direction == 'middle' and events[-1].action == 'released':
        #    metronome_on = False
        # increment count after every wait and beat after ever 4 counts
        count += 1
        if count > mode:
            count = 1
            beat += 1
            # set metronome audio according to beat count
            #wave_obj = simpleaudio.WaveObject.from_wave_file('./metronome/metronome.wav')
        
        #channel1.play(metronome_sound)
        #if count == 1:
        #    channel2.play(metronome_up)
        
        wave_obj = simpleaudio.WaveObject.from_wave_file('./metronome/metronome.wav')
        if count == 1:
            wave_obj = simpleaudio.WaveObject.from_wave_file('./metronome/metronomeup.wav')
        exec_time = time.time()-start
        play_obj = wave_obj.play()
        wait(delay-0.007)
            
sensehat = SenseHat()
play_metronome(wav_path=music_path)