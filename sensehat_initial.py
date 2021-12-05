import time
import os
import sys, math, wave, numpy, pygame
#from sense_hat import SenseHat
from sense_emu import SenseHat
import glob
from time import sleep
from random import randint
import numpy as np


# get current time
curr_time = time.localtime()
curr_clock = time.strftime("%H:%M:%S", curr_time)
# greeting
if int(curr_clock.split(':')[0])<=12:
    greeting = 'Guten Morgen'
elif int(curr_clock.split(':')[0])<17:
    greeting = "Guten Nachmittag"
else:
    greeting = 'Guten Abend'
    
sense = SenseHat()

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
sense.show_message("{}, Martin! :)".format(greeting), 0.05, color, background)

#sense.show_message("1")

pygame.mixer.init()
# Get a list of all the music files
path_to_music = "/home/pi/Music"
os.chdir(path_to_music)
music_files = glob.glob("*.mp3")
music_files.sort()

volume = 1.0
current_track = 0
no_tracks = len(music_files)

pygame.mixer.music.load(music_files[current_track])
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play()
start_time = 0.0
sense.set_pixels(love_pixels)
pygame.time.Clock().tick()
