import librosa
from pysndfx import AudioEffectsChain
import python_speech_features



def read_file(file_name):
    sample_file = file_name
    sample_directory = 'lectures/'
    sample_path = sample_directory + sample_file

    # generating audio time series and a sampling rate (int)
    a, sr = librosa.load(sample_path)

    return a, sr


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

    return (a_speach_boosted)

def mfcc_lowshelf(a, sr):

    mfcc = python_speech_features.base.mfcc(a)
    mfcc = python_speech_features.base.logfbank(a)
    mfcc = python_speech_features.base.lifter(mfcc)

    sum_of_squares = []
    index = -1
    for x in mfcc:
        sum_of_squares.append(0)
        index = index + 1
        for n in x:
            sum_of_squares[index] = sum_of_squares[index] + n**2

    strongest_frame = sum_of_squares.index(max(sum_of_squares))
    hz = python_speech_features.base.mel2hz(mfcc[strongest_frame])

    max_hz = max(hz)
    min_hz = min(hz)

    speech_booster = AudioEffectsChain().lowshelf(frequency=min_hz*(-1), gain=12.0, slope=0.5)
    a_speach_boosted = speech_booster(a)

    return (a_speach_boosted)


def trim_silence(y):
    a_trimmed, index = librosa.effects.trim(y, top_db=20, frame_length=2, hop_length=500)
    trimmed_length = librosa.get_duration(y) - librosa.get_duration(a_trimmed)

    return a_trimmed, trimmed_length


def enhance(y):
    apply_audio_effects = AudioEffectsChain().lowshelf(gain=10.0, frequency=260, slope=0.1).reverb(reverberance=25, hf_damping=5, room_scale=5, stereo_depth=50, pre_delay=20, wet_gain=0, wet_only=False)#.normalize()
    a_enhanced = apply_audio_effects(y)

    return a_enhanced

def output_file(destination ,filename, a, sr, ext=""):
    destination = destination + filename[:-4] + ext + '.wav'
    librosa.output.write_wav(destination, a, sr)


lectures = ['Lecture01.wav']

for s in lectures:
    filename = s
    a, sr = read_file(filename)


    # a_reduced_centroid_s = reduce_noise_centroid_s(a, sr)
    a_reduced_mfcc_lowshelf = mfcc_lowshelf(a, sr)
    a_reduced_mfcc_highshelf = mffc_highshelf(a, sr)


    # trimming silences
    # a_reduced_centroid_s, time_trimmed = trim_silence(a_reduced_centroid_s)
    a_reduced_mfcc_up, time_trimmed = trim_silence(mfcc_lowshelf)
    a_reduced_mfcc_down, time_trimmed = trim_silence(mffc_highshelf)



    # output_file('lectures_trimmed_noise_reduced/' ,filename, y_reduced_centroid_s, sr, '_ctr_s')
    output_file('lectures_trimmed_noise_reduced/' ,filename, a_reduced_mfcc_up, sr, '_mfcc_up')
    # output_file('lectures_trimmed_noise_reduced/' ,filename, a_reduced_mfcc_down, sr, '_mfcc_down')
    # output_file('lectures_trimmed_noise_reduced/' ,filename, a, sr, '_org')
