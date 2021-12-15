import simpleaudio
import random
import time
import pygame

def wait(delay):
    end_time = time.time() + delay
    while end_time > time.time():
        continue


def metronome(bpm, track_path):
    print(float(bpm), "bpm")
    delay = 60/bpm
    count = 0
    beat = 0

    mode = 4
    multiple = 8
    pygame.init()
    pygame.mixer.init(44100, -16, 2, 64)
    pygame.mixer.music.load(track_path)
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play()

    #upbeat
    # wait(0-0.01)
    while True:
        # increment count after every wait and beat after ever 4 counts
        count += 1
        if count > mode:
            count = 1
            beat += 1

        # set metronome audio according to beat count
        wave_obj = simpleaudio.WaveObject.from_wave_file('metronome.wav')
        if count == 1:
            wave_obj = simpleaudio.WaveObject.from_wave_file('metronomeup.wav')

        # play metronome audio
        play_obj = wave_obj.play()

        # Remove this after testing
        wait(delay-0.01)

metronome(123, '/home/pi/pythonproject/raspberrypi_sensehat_music/Music/Parcels/Lightenup.wav')