import librosa
from pysndfx import AudioEffectsChain
import python_speech_features
import os


def noise_removal(video_name):

    # sample_file = file_name
    # sample_directory = 'lectures/'
    # sample_path = sample_directory + sample_file

    print('starting the noise removal process')


    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LECTURE_VIDEO_DIR = os.path.join(BASE_DIR, "lectures\\{}".format(video_name))
    print('lecture audio directory: ', LECTURE_VIDEO_DIR)
    # DESTINATION_DIR = os.path.join(BASE_DIR, "LectureSummarizingApp\\noise_removed_lectures")
    DESTINATION_DIR = os.path.dirname(os.path.join(BASE_DIR, "noise_removed_lectures\\sample.txt"))
    print('destination directory: ', DESTINATION_DIR)
    # generating audio time series and a sampling rate (int)
    a, sr = librosa.load(path=LECTURE_VIDEO_DIR)

    print('a: ', a)
    print('sr: ', sr)

    # speech_boosted = mffc_highshelf(a, sr)

    output_file(destination=DESTINATION_DIR, filename=video_name, a=a, sr=sr)

    print('ending the noise removal process')


'''MFCC'''

def mffc_highshelf(a, sr):


    mfcc = python_speech_features.base.mfcc(a)
    mfcc = python_speech_features.base.logfbank(a)
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
    a_speach_boosted = speech_booster(a)
    # a_speach_boosted = speech_booster.

    return (a_speach_boosted)


# def trim_silence(y):
#     a_trimmed, index = librosa.effects.trim(y, top_db=20, frame_length=2, hop_length=500)
#     trimmed_length = librosa.get_duration(y) - librosa.get_duration(a_trimmed)
#
#     return a_trimmed, trimmed_length


# def enhance(y):
#     apply_audio_effects = AudioEffectsChain().lowshelf(gain=10.0, frequency=260, slope=0.1).reverb(reverberance=25, hf_damping=5, room_scale=5, stereo_depth=50, pre_delay=20, wet_gain=0, wet_only=False)#.normalize()
#     a_enhanced = apply_audio_effects(y)
#
#     return a_enhanced

def output_file(destination ,filename, a, sr, ext=""):
    destination = destination + "\\" + filename[:-4] + ext + '.wav'
    print('output destination: ', destination)
    librosa.output.write_wav(destination, a, sr)

