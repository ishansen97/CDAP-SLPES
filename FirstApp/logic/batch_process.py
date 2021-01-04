import requests


def batch_process(video_id, video_name):


    # call the activity process
    activity_resp = requests.get('http://127.0.0.1:8000/process-lecture-activity/?lecture_video_name=' + video_name + '&lecture_video_id=' + video_id)

    # call the emotion process
    emotion_resp = requests.get('http://127.0.0.1:8000/process-lecture-emotion/?lecture_video_name=' + video_name + '&lecture_video_id=' + video_id)

    # call the gaze process
    gaze_resp = requests.get('http://127.0.0.1:8000/process-lecture-gaze-estimation/?lecture_video_name=' + video_name + '&lecture_video_id=' + video_id)


    pass


# this method will save the lecture video
def save_student_lecture_video(student_video):

    # call the API
    student_video_save_resp = requests.post('http://127.0.0.1:8000/lecture-video', student_video)