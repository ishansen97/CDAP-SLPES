import json

import requests

# this method calls all the summarization methods in one place
def summarization_batch_process(audio_id, audio_name):


    is_all_processed = False

    noise_removed_resp = requests.get('http://127.0.0.1:800/summary/lecture-audio-noise-removed', params={'id': audio_id, 'audio_name': audio_name})


    if noise_removed_resp.json()['response'] == 200:

        audio_root_name = audio_name.split('.')[0]
        speech_to_text_name = audio_root_name + '.txt'

        audio_text_resp = requests.get('http://127.0.0.1:800/summary/lecture-audio-to-text', params={'id': audio_id, 'speech_to_text_name': speech_to_text_name})

        if audio_text_resp.json()['response'] == 200:

            summary_name = audio_name + '.txt'
            summary_resp = requests.get('http://127.0.0.1:800/summary/lecture-summary', params={'id': audio_id, 'lecture_summary_name': summary_name})

            if summary_resp.json()['response'] == 200:

                notice_resp = requests.get('http://127.0.0.1:800/summary/lecture-notices', params={'id': audio_id, 'lecture_notice_name': summary_name})

                if notice_resp.json()['response'] == 200:
                    is_all_processed = True


    return is_all_processed



def save_lecturer_audio(lecturer_audio):

    data_dumps = json.dumps(lecturer_audio)
    response = None

    headers = {
        'Content-Type': 'application/json'
    }

    # call the API
    # student_video_save_resp = requests.post('http://127.0.0.1:8000/lecture-video', student_video)
    lecturer_audio_save_resp = requests.post(url='http://127.0.0.1:8000/summary/lecture-audio', data=data_dumps, headers=headers)

    data = lecturer_audio_save_resp.json()
    response = data[0]

    return response


# this is a test method (delete later)
if __name__ == '__main__':
    audio_id = 1
    audio_name = 'Lecture01.wav'

    summarization_batch_process(audio_id=audio_id, audio_name=audio_name)