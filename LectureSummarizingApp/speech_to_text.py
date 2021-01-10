import speech_recognition as sr
import os


def speech_to_text(speech_to_text_name):

    print('starting the speech_to_text process')
#calling the Recognizer()
    r = sr.Recognizer()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # FILE_PATH = os.path.join(BASE_DIR, "noise_removed_lectures\\noise_removed_lectures_{}".format(speech_to_text_name))
    FILE_PATH = os.path.join(BASE_DIR, "noise_removed_lectures\\{}".format(speech_to_text_name))
    print('file path: ', FILE_PATH)
    # DESTINATION_DIR = os.path.dirname(os.path.join(BASE_DIR, "LectureSummarizingApp\\speechToText\\{}.txt".format(speech_to_text_name)))
    DESTINATION_DIR = os.path.join(BASE_DIR, "speechToText\\{}.txt".format(speech_to_text_name))
    print('destination directory: ', DESTINATION_DIR)

    with sr.AudioFile(FILE_PATH) as source:
        audio = r.listen(source)
        # file = open('audioToText01.txt', 'w') #open file
        file = open(DESTINATION_DIR, 'w') #open file
        try:
            text = r.recognize_google(audio) #Convert using google recognizer
            file.write(text)
        except:
            file.write('error')

        file.close()

    print('ending the speech_to_text process')

    return True
