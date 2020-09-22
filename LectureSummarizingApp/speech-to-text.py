import speech_recognition as sr

r = sr.Recognizer()

with sr.AudioFile('female.wav') as source:
    audio = r.listen(source)
    file = open('audioToText01.txt', 'w')
    try:
        text = r.recognize_google(audio)
        file.write(text)
    except:
        file.write('error')

    file.close()