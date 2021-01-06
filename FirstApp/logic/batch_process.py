import requests
import json


def student_behavior_batch_process(video_id, video_name):


    is_all_processed = False

    # call the activity process
    activity_resp = requests.get('http://127.0.0.1:8000/process-lecture-activity/', params={'lecture_video_name': video_name, 'lecture_video_id': video_id})

    # if the activity process is success
    if activity_resp.json()['response']:

        # call the emotion process
        emotion_resp = requests.get('http://127.0.0.1:8000/process-lecture-emotion/?lecture_video_name=', params={'lecture_video_name': video_name, 'lecture_video_id': video_id})

        # if the emotion process is success
        if emotion_resp.json()['response']:

            # call the gaze process
            gaze_resp = requests.get('http://127.0.0.1:8000/process-lecture-gaze-estimation/?lecture_video_name=', params={'lecture_video_name': video_name, 'lecture_video_id': video_id})

            # if the gaze estimation process is successful
            if gaze_resp.json()['response']:
                is_all_processed = True

    return is_all_processed


# this method will save the lecture video
def save_student_lecture_video(student_video):

    data_dumps = json.dumps(student_video)

    headers = {
        'Content-Type': 'application/json'
    }

    # call the API
    # student_video_save_resp = requests.post('http://127.0.0.1:8000/lecture-video', student_video)
    student_video_save_resp = requests.post(url='http://127.0.0.1:8000/lecture-video', data=data_dumps, headers=headers)

    data = student_video_save_resp.json()

    return data[0]


if __name__ == '__main__':
    # content = {
    #     "lecturer": 1,
    #     "subject": 16,
    #     "date": "2020-12-09",
    #     "video_name": "Video_test_19.mp4",
    #     "video_length": "00:45:06"
    # }
    #
    #
    # data_dumps = json.dumps(content)
    # data_json = json.loads(data_dumps)
    #
    #
    # save_student_lecture_video(content)

    student_behavior_batch_process(8, "Video_test_8.mp4")

