import numpy as nump
import scipy as sip
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from scipy import signal
import matplotlib.pyplot as mplt
#get_ipython().magic('matplotlib inline')

(Frequency, array) = read('lectures/Lecture01.wav')

len(array)

mplt.plot(array)
mplt.title('Original Signal Spectrum')
mplt.xlabel('Frequency(Hz)')
mplt.ylabel('Amplitude')

fourierTransformation = sip.fft(array)

scale = sip.linspace(0, Frequency, len(array))

mplt.stem(scale[0:5000], nump.abs(fourierTransformation[0:5000]), 'r')
mplt.title('Signal spectrum after FFT')
mplt.xlabel('Frequency(Hz)')
mplt.ylabel('Amplitude')


guassianNoise = nump.random.rand(len(fourierTransformation))


NewSound = guassianNoise + array

write("New-Sound-Added-With-Guassian-Noise.wav", Frequency, NewSound)

u,v = signal.butter(5, 1000/(Frequency/2), btype='highpass')

filteredSignal = signal.lfilter(u,v,NewSound)

# plotting the signal.
mplt.plot(filteredSignal)
mplt.title('Highpass Filter')
mplt.xlabel('Frequency(Hz)')
mplt.ylabel('Amplitude')

# ButterWorth low-filter
x,y = signal.butter(5, 380/(Frequency/2), btype='lowpass')

# Applying the filter to the signal
newFilteredSignal = signal.lfilter(x,y,filteredSignal)

# plotting the signal.
mplt.plot(newFilteredSignal)
mplt.title('Lowpass Filter')
mplt.xlabel('Frequency(Hz)')
mplt.ylabel('Amplitude')

write("removed.wav", Frequency, nump.int16(newFilteredSignal/nump.max(nump.abs(newFilteredSignal)) * 32767))