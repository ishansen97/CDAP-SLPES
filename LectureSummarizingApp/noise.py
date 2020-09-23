import librosa
from pysndfx import AudioEffectsChain
import numpy as np
import math
import python_speech_features
import scipy as sp
from scipy import signal
import soundfile


def read_file(file_name):
    sample_file = file_name
    sample_directory = 'lectures/'
    sample_path = sample_directory + sample_file

    # generating audio time series and a sampling rate (int)
    y, sr = librosa.load(sample_path)

    return y, sr


# '''CENTROID'''
#
# def reduce_noise_centroid_s(y, sr):
#
#     cent = librosa.feature.spectral_centroid(y=y, sr=sr)
#     threshold_h = np.max(cent)
#     threshold_l = np.min(cent)
#     less_noise = AudioEffectsChain().lowshelf(gain=-12.0, frequency=threshold_l, slope=0.5).highshelf(gain=-12.0, frequency=threshold_h, slope=0.5).limiter(gain=6.0)
#     y_cleaned = less_noise(y)
#     return y_cleaned



'''MFCC'''

def mffc_highshelf(y, sr):


    mfcc = python_speech_features.base.mfcc(y)
    mfcc = python_speech_features.base.logfbank(y)
    mfcc = python_speech_features.base.lifter(mfcc)

    sum_of_squares = []
    index = -1
    for r in mfcc:
        sum_of_squares.append(0)
        index = index + 1
        for n in r:
            sum_of_squares[index] = sum_of_squares[index] + n**2

    strongest_frame = sum_of_squares.index(max(sum_of_squares))
    hz = python_speech_features.base.mel2hz(mfcc[strongest_frame])

    max_hz = max(hz)
    min_hz = min(hz)

    speech_booster = AudioEffectsChain().highshelf(frequency=min_hz*(-1)*1.2, gain=-12.0, slope=0.6).limiter(gain=8.0)
    y_speach_boosted = speech_booster(y)

    return (y_speach_boosted)

def mfcc_lowshelf(y, sr):

    mfcc = python_speech_features.base.mfcc(y)
    mfcc = python_speech_features.base.logfbank(y)
    mfcc = python_speech_features.base.lifter(mfcc)

    sum_of_squares = []
    index = -1
    for r in mfcc:
        sum_of_squares.append(0)
        index = index + 1
        for n in r:
            sum_of_squares[index] = sum_of_squares[index] + n**2

    strongest_frame = sum_of_squares.index(max(sum_of_squares))
    hz = python_speech_features.base.mel2hz(mfcc[strongest_frame])

    max_hz = max(hz)
    min_hz = min(hz)

    speech_booster = AudioEffectsChain().lowshelf(frequency=min_hz*(-1), gain=12.0, slope=0.5)
    y_speach_boosted = speech_booster(y)

    return (y_speach_boosted)


def trim_silence(y):
    y_trimmed, index = librosa.effects.trim(y, top_db=20, frame_length=2, hop_length=500)
    trimmed_length = librosa.get_duration(y) - librosa.get_duration(y_trimmed)

    return y_trimmed, trimmed_length


def enhance(y):
    apply_audio_effects = AudioEffectsChain().lowshelf(gain=10.0, frequency=260, slope=0.1).reverb(reverberance=25, hf_damping=5, room_scale=5, stereo_depth=50, pre_delay=20, wet_gain=0, wet_only=False)#.normalize()
    y_enhanced = apply_audio_effects(y)

    return y_enhanced

def output_file(destination ,filename, y, sr, ext=""):
    destination = destination + filename[:-4] + ext + '.wav'
    librosa.output.write_wav(destination, y, sr)


lectures = ['Lecture01.wav']

for s in lectures:
    filename = s
    y, sr = read_file(filename)


    # y_reduced_centroid_s = reduce_noise_centroid_s(y, sr)
    y_reduced_mfcc_lowshelf = mfcc_lowshelf(y, sr)
    y_reduced_mfcc_highshelf = mffc_highshelf(y, sr)


    # trimming silences
    # y_reduced_centroid_s, time_trimmed = trim_silence(y_reduced_centroid_s)
    y_reduced_mfcc_up, time_trimmed = trim_silence(mfcc_lowshelf)
    y_reduced_mfcc_down, time_trimmed = trim_silence(mffc_highshelf)



    # output_file('lectures_trimmed_noise_reduced/' ,filename, y_reduced_centroid_s, sr, '_ctr_s')
    output_file('lectures_trimmed_noise_reduced/' ,filename, y_reduced_mfcc_up, sr, '_mfcc_up')
    # output_file('lectures_trimmed_noise_reduced/' ,filename, y_reduced_mfcc_down, sr, '_mfcc_down')
    # output_file('lectures_trimmed_noise_reduced/' ,filename, y, sr, '_org')
