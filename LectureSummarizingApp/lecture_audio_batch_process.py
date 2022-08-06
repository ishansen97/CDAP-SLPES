import json

import requests

# this method calls all the summarization methods in one place
def summarization_batch_process(audio_id, audio_name):


    is_all_processed = False
    summary_id = ''


    noise_removed_resp = requests.get('http://127.0.0.1:8000/summary/lecture-noise/', params={'id': audio_id, 'audio_name': audio_name})

    print('response: ', noise_removed_resp.json())

    if noise_removed_resp.json()['response'] == 200:

        print('successful noise removed response')

        audio_root_name = audio_name.split('.')[0]
        speech_to_text_name = audio_root_name + '.txt'

        audio_text_resp = requests.get('http://127.0.0.1:8000/summary/lecture-text/', params={'id': audio_id, 'speech_to_text_name': speech_to_text_name})

        if audio_text_resp.json()['response'] == 200:

            print('successful audio to text response')

            summary_name = audio_name.split('.')[0] + '.txt'
            summary_resp = requests.get('http://127.0.0.1:8000/summary/lecture-summary/', params={'id': audio_id, 'lecture_summary_name': summary_name})


            if summary_resp.json()['response'] == 200:

                summary_id = summary_resp.json()['summary_id']

                print('successful summary response')

                notice_resp = requests.get('http://127.0.0.1:8000/summary/lecture-notices/', params={'id': audio_id, 'lecture_notice_name': summary_name})

                if notice_resp.json()['response'] == 200:
                    print('successful notice response')
                    is_all_processed = True


    return is_all_processed, summary_id



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
    response = data

    return response


# # this is a test method (delete later)
# if __name__ == '__main__':
#     audio_id = 1
#     audio_name = 'Lecture01.wav'
#
#     summarization_batch_process(audio_id=audio_id, audio_name=audio_name)