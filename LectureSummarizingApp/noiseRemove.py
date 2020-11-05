import numpy as np
import scipy as sp
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from scipy import signal
import matplotlib.pyplot as plt
#get_ipython().magic('matplotlib inline')

(Frequency, array) = read('lectures/Lecture01.wav')

len(array)

plt.plot(array)
plt.title('Original Signal Spectrum')
plt.xlabel('Frequency(Hz)')
plt.ylabel('Amplitude')

FourierTransformation = sp.fft(array)

scale = sp.linspace(0, Frequency, len(array))

plt.stem(scale[0:5000], np.abs(FourierTransformation[0:5000]), 'r')
plt.title('Signal spectrum after FFT')
plt.xlabel('Frequency(Hz)')
plt.ylabel('Amplitude')


GuassianNoise = np.random.rand(len(FourierTransformation))


NewSound = GuassianNoise + array

write("New-Sound-Added-With-Guassian-Noise.wav", Frequency, NewSound)

b,a = signal.butter(5, 1000/(Frequency/2), btype='highpass')

filteredSignal = signal.lfilter(b,a,NewSound)
plt.plot(filteredSignal) # plotting the signal.
plt.title('Highpass Filter')
plt.xlabel('Frequency(Hz)')
plt.ylabel('Amplitude')

c,d = signal.butter(5, 380/(Frequency/2), btype='lowpass') # ButterWorth low-filter
newFilteredSignal = signal.lfilter(c,d,filteredSignal) # Applying the filter to the signal
plt.plot(newFilteredSignal) # plotting the signal.
plt.title('Lowpass Filter')
plt.xlabel('Frequency(Hz)')
plt.ylabel('Amplitude')

write("file.wav", Frequency, np.int16(newFilteredSignal/np.max(np.abs(newFilteredSignal)) * 32767))