import time
import os
import sys, math, wave, numpy, pygame
from sense_hat import SenseHat
import subprocess as sp
#from sense_emu import SenseHat
import glob
from time import sleep
from random import randint
import numpy as np
from pygame.locals import *
from scipy.fftpack import dct

PIXEL_SIZE = 8 
FPS = 10

sense = SenseHat()
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
background = (0,0,0)
R = (198, 30, 74)       #raspberrytips red
W = (255, 255, 255)     #white

def draw_pixels_random(pixels, maintain_sec=2):
    pixel_state = np.array([0]*64)
    #set one pixel at at time
    while set(pixel_state)!={1}:
        X = randint(0,7)
        Y = randint(0,7)
        if pixel_state[(X+1)+Y*8-1] == 1:
            continue
        else:
            sense.set_pixel(X, Y, pixels[(X+1)+Y*8-1])
            pixel_state[(X+1)+Y*8-1] = 1
            sleep(0.02)
    sleep(maintain_sec)

#set all pixels at once
love_pixels = [
     W, W, W, W, W, W, W, W,
     W, R, R, W, R, R, W, W,
     R, R, R, R, R, R, R, W,
     R, R, R, R, R, R, R, W,
     R, R, R, R, R, R, R, W,
     W, R, R, R, R, R, W, W,
     W, W, R, R, R, W, W, W,
     W, W, W, R, W, W, W, W
]

draw_pixels_random(love_pixels)
#set one pixel at at time
sense.clear()
#sense.show_message("{}, Martin! :)".format(greeting), 0.05, W, background)

file_name = 'lightenup'
status = 'stopped'
volume = 5
#fpsclock = pygame.time.Clock()

#screen init, music playback
pygame.mixer.init()
# Get a list of all the music files
path_to_music = "/home/pi/Music"
os.chdir(path_to_music)
music_files = glob.glob("*.mp3")
music_files.sort()
fpsclock = pygame.time.Clock()
volume = 1.0
current_track = 0
no_tracks = len(music_files)

x_axis_color_dict_parcels = {6:tuple((218, 217, 218)),
                             7:tuple((218, 217, 218)),
                             0:tuple((42, 75, 114)),
                             1:tuple((42, 75, 114)),
                             2:tuple((114, 85, 62)),
                             3:tuple((114, 85, 62)),
                             4:tuple((133, 152, 172)),
                             5:tuple((133, 152, 172))}



#process wave data
filename, extension = os.path.splitext(music_files[current_track])
print(filename, extension)
if extension != "wav":
    fnull = open(os.devnull, "w")
    pieq_tmp = os.path.expanduser("~") + "/.pieq_tmp/"
    wav_path = pieq_tmp + filename + ".wav"
    if not os.path.isfile(wav_path):
        print("Decompressing...")
        sp.call(["mkdir", "-p", pieq_tmp])
        sp.call(["ffmpeg", "-i", music_files[current_track], wav_path], stdout=fnull, stderr=sp.STDOUT)
        tmp_file_created = True
else:
    tmp_file_created = False
    wav_path = music_files[current_track]
f = wave.open(wav_path, 'rb')
params = f.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]
str_data = f.readframes(nframes)
f.close()
wave_data = numpy.frombuffer(str_data, dtype = numpy.short)
wave_data.shape = -1, 2
wave_data = wave_data.T
num = nframes


pygame.mixer.music.load(wav_path)
pygame.mixer.music.set_volume(volume)    
pygame.mixer.music.play()
start_time = 0.0
pygame.time.Clock().tick()
status = 'playing'

def Visualizer(nums):
    nums = int(nums)
    h = abs(dct(wave_data[0][nframes - nums:nframes - nums + PIXEL_SIZE],2))
    h = [min(PIXEL_SIZE, int(i**(1 / 2.5) * PIXEL_SIZE/ 100)+1) for i in h]
    draw_bars_pixels(h, x_color_dict=x_axis_color_dict_parcels)

def vis(status):
    global num
    if status == "stopped":
        num = nframes
        return
    elif status == "paused":
        Visualizer(num)
    else:
        num -= framerate / FPS
        if num > 0:
            Visualizer(num)

def get_time():
    seconds = max(0, pygame.mixer.music.get_pos() / 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    hms = ("%02d:%02d:%02d" % (h, m, s))
    return hms

def controller(key):
    global status
    if status == "stopped":
        if key == K_RETURN:
            pygame.mixer_music.play()
            status = "playing"
    elif status == "paused":
        if key == K_RETURN:
            pygame.mixer_music.stop()
            status = "stopped"
        elif key == K_SPACE:
            pygame.mixer.music.unpause()
            status = "playing"
    elif status == "playing":
        if key == K_RETURN:
            pygame.mixer.music.stop()
            status = "stopped"
        elif key == K_SPACE:
            pygame.mixer.music.pause()
            status = "paused"
        
def draw_bars_pixels(h, bgd_clr=(0,0,0), fill_clr=(255,255,255), x_color_dict=None):
    matrix = [bgd_clr]*64
    np_matrix = np.array(matrix).reshape(8,8,3)
    for i in range(len(h)):
        if x_color_dict is not None:
            fill_clr = x_color_dict[i]
        np_matrix[i][(8-h[i]):] = fill_clr
    # update column by column
    for X in range(0,8):
        for Y in range(0,8):
            sense.set_pixel(X,Y,np_matrix[X][Y])
    #pixel_list = [tuple(i) for i in np_matrix.reshape(64,3).tolist()]
    

while True:
    if num <= 0:
        status = "stopped"
    fpsclock.tick(FPS)
    vis(status)

