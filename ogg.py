#!/usr/bin/python3

import os
import time
import argparse
import platform
import ctypes
import ctypes.util
import sys
import signal
import subprocess
import pyogg
import openal
import simpleaudio
import time
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('file', metavar='file', help='vorbis (.ogg) file to play', type=str)
parser.add_argument('-s', '--simpleaudio', help='play via simpleaudio', required=False, action='store_true')
args, unknown_args = parser.parse_known_args()

# load and decode compressed file to raw samples
file = pyogg.VorbisFile(args.file)
print("\nRead Ogg Vorbis file")
print("Channels:\n  ", file.channels)
print("Frequency (samples per second):\n  ", file.frequency)
print("Buffer Length (bytes):\n  ", len(file.buffer))
audio_data = file.as_array()
print("Shape of numpy array (number of samples per channel, number of channels):\n  ", audio_data.shape)

#play decoded data in different ways

if args.simpleaudio:
    # play via simpleaudio
    play_obj = simpleaudio.play_buffer(audio_data, file.channels, file.bytes_per_sample, file.frequency)
    while play_obj.is_playing():
        time.sleep(0.1)
else:
    #play via openAL
    device = openal.alcOpenDevice(None)
    if not device:
        error = alc.alcGetError()
        # TODO: do something with the error, which is a ctypes value
        exit(-1)
    print(openal.alcGetString(device, openal.ALC_DEVICE_SPECIFIER))
    context = openal.alcCreateContext(device, None)
    openal.alcMakeContextCurrent(context)
    source = openal.ALuint()
    openal.alGenSources(1, source)
    openal.alSource3f(source, openal.AL_POSITION, 0, 0, 0)
    openal.alSource3f(source, openal.AL_VELOCITY, 0, 0, 0)
    openal.alSourcei(source, openal.AL_LOOPING, 0)
    error = openal.alcGetError(device)
    assert not error
    buffer = openal.ALuint()
    openal.alGenBuffers(1, buffer)
    print(audio_data.ctypes.data_as(ctypes.c_void_p))
    print(file.bytes_per_sample * 2 * 2)
    openal.alBufferData(buffer, openal.AL_FORMAT_STEREO16, audio_data.ctypes.data_as(ctypes.c_void_p), len(file.buffer), file.frequency)
    openal.alSourceQueueBuffers(source, 1, buffer)
    openal.alSourcePlay(source)
    # wait for the source to finish
    print('playing ...')
    state = openal.ALint(0)
    play_pos = openal.ALfloat(0)
    while True:
        # AL_SEC_OFFSET AL_SAMPLE_OFFSET
        openal.alGetSourcef(source, openal.AL_SEC_OFFSET, play_pos)
        print('sec=', play_pos.value)
        openal.alGetSourcei(source, openal.AL_SOURCE_STATE, state)
        if state.value != openal.AL_PLAYING:
            break
        else:
            time.sleep(0.1)
    print('finished.')
    openal.alSourcei(source, openal.AL_BUFFER, 0)
    # clean up
    openal.alDeleteBuffers(1, buffer)
    openal.alDeleteSources(1, source)
    openal.alcDestroyContext(context)
    openal.alcCloseDevice(device)
