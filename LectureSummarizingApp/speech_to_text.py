import speech_recognition as sr
import os


def speech_to_text(video_name):

    r = sr.Recognizer()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    VIDEO_PATH = os.path.join(BASE_DIR, "lectures\\{}".format(video_name))

    with sr.AudioFile(VIDEO_PATH) as source:
        audio = r.listen(source)
        file = open('audioToText01.txt', 'w')
        try:
            text = r.recognize_google(audio)
            file.write(text)
        except:
            file.write('error')

        file.close()