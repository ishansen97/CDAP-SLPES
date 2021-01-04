import requests

# this method lists down the main methods that need to be executed when the lecturer performance module is under operation
def lecturer_batch_process(video_name, audio_name):

    # As the first step, calculate the lectuer activity details
    lecturer_activity_resp = requests.get('http://127.0.0.1:8000/activities/?video_name=' + video_name)

    # save the lecturer video frame recognitions
    lecturer_video_frame_recognitions_resp = requests.get('http://127.0.0.1:8000/process-lecturer-video-frame-recognitions/?video_name=' + video_name)

    # processing the lecture audio
    lecture_audio_text_resp = requests.get('http://127.0.0.1:8000/lecturer/process-lecture-audio-analysis')


# this method will save the lecturer video details
def save_lecturer_video_details(video):

    lecturer_video_resp = requests.post('http://127.0.0.1:8000/lecturer-video', video)