import requests
import json

# this method lists down the main methods that need to be executed when the lecturer performance module is under operation
def lecturer_batch_process(video_name, audio_name):

    is_all_processed = False

    # As the first step, calculate the lectuer activity details
    # lecturer_activity_resp = requests.get('http://127.0.0.1:8000/activities/?video_name=' + video_name)
    lecturer_activity_resp = requests.get('http://127.0.0.1:8000/activities/', params={'video_name': video_name})

    # if the lecturer activity is created
    if lecturer_activity_resp.json()['created']:

        # save the lecturer video frame recognitions
        # lecturer_video_frame_recognitions_resp = requests.get('http://127.0.0.1:8000/process-lecturer-video-frame-recognitions/?video_name=' + video_name)
        lecturer_video_frame_recognitions_resp = requests.get('http://127.0.0.1:8000/process-lecturer-video-frame-recognitions/', params={'video_name': video_name})

        # if the lecture video frame recognitions are created
        if lecturer_video_frame_recognitions_resp.json()['created']:

            # processing the lecture audio
            lecture_audio_text_resp = requests.get('http://127.0.0.1:8000/lecturer/process-lecture-audio-analysis')

            # if the lecturer audio text is processed
            if lecture_audio_text_resp.json()['created']:
                is_all_processed = True


    return is_all_processed

# this method will save the lecturer video details
def save_lecturer_video_details(video):


    headers = {
        "Content-Type": "application/json"
    }

    # convert the data into JSON string
    video_json_str = json.dumps(video)

    lecturer_video_resp = requests.post(url='http://127.0.0.1:8000/lecturer/lecturer-video/', data=video_json_str, headers=headers)

    response = lecturer_video_resp.json()

    return response[0]


if __name__ == '__main__':

    video = {
        "lecturer": 1,
        "subject": 16,
        "lecturer_date": "2020-12-09",
        "lecture_video_name": "Video_test_19.mp4",
        "lecture_video_length": "00:45:06"
    }

    response = save_lecturer_video_details(video)

    print('response: ', response)