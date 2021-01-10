import requests
import json

from LectureSummarizingApp.lecture_audio_batch_process import save_lecturer_audio, summarization_batch_process
from MonitorLecturerApp.logic.lecturer_batch_process import lecturer_batch_process
from .MongoModels import LectureVideo
from . logic import batch_process as bp
from MonitorLecturerApp.logic import lecturer_batch_process as lbp
import datetime


# this method will save the lecture video

#
# def save_student_lecture_video(student_video):
#
#     data_dumps = json.dumps(student_video)
#
#     headers = {
#         'Content-Type': 'application/json'
#     }
#
#     # call the API
#     # student_video_save_resp = requests.post('http://127.0.0.1:8000/lecture-video', student_video)
#     student_video_save_resp = requests.post(url='http://127.0.0.1:8000/lecture-video', data=data_dumps, headers=headers)
#
#     data = student_video_save_resp.json()
#
#     return data[0]
#
#
# # this method will save the lecturer video details
# def save_lecturer_video_details(video):
#
#
#     headers = {
#         "Content-Type": "application/json"
#     }
#
#     # convert the data into JSON string
#     video_json_str = json.dumps(video)
#
#     lecturer_video_resp = requests.post(url='http://127.0.0.1:8000/lecturer/lecturer-video/', data=video_json_str, headers=headers)
#
#     response = lecturer_video_resp.json()
#
#     return response[0]

# this method will handle the batch processing and video/audio saving pf the system
from .logic.batch_process import student_behavior_batch_process
from .serializers import LectureVideoSerializer


# @background(schedule=5)
def automation_process(lecturer, subject, subject_code, video_length="00:20:00"):

    current_date = datetime.datetime.now().date()

    # this variable will be returned
    is_all_processed = False

    # define the video/audio names to be saved
    student_video_name = str(current_date) + "_{}_student_video.mp4".format(subject_code)
    lecturer_video_name = str(current_date) + "_{}_lecturer_video.mp4".format(subject_code)
    lecturer_audio_name = str(current_date) + "_{}_lecturer_audio.wav".format(subject_code)


    # this variable will be passed in the individual batch process
    student_video_id = 0

    # create the student video content
    student_video_content = {
        "lecturer": lecturer,
        "subject": subject,
        "date": str(current_date),
        "video_name": student_video_name,
        "video_length": video_length

    }

    # create the student video content
    lecturer_video_content = {
        "lecturer": lecturer,
        "subject": subject,
        "lecturer_date": str(current_date),
        "lecture_video_name": lecturer_video_name,
        "lecture_video_length": video_length
    }

    # create the lecturer audio content
    lecturer_audio_content = {
        "lecturer": lecturer,
        "subject": subject,
        "audio_name": lecturer_audio_name
    }



    # save the student video
    student_video_response = bp.save_student_lecture_video(student_video_content)
    # student_video_response = save_student_lecture_video(student_video_content)
    print('student video response: ', student_video_response)
    student_video_id = student_video_response['id']

    # save the lecturer video
    lecturer_video_response = lbp.save_lecturer_video_details(lecturer_video_content)
    # lecturer_video_response = save_lecturer_video_details(lecturer_video_content)
    print('lecturer video response: ', lecturer_video_response)

    # save the lecturer audio
    lecturer_audio_response = save_lecturer_audio(lecturer_audio_content)
    audio_id = lecturer_audio_response['audio_id']

    # for i in range(100):
    #     print('outer loop: ', i)
    #
    #     for j in range(10000):
    #         print('inner loop: ', j)


    # start the batch processing for lecture summarization component
    lecture_summary_batch_process = summarization_batch_process(audio_id, lecturer_audio_name)

    # if the lecture summarization process is successful
    if lecture_summary_batch_process:

        # start the batch processing for monitoring lecturer performance component
        lecturer_batch_process_response = lecturer_batch_process(lecturer_video_name, lecturer_audio_name)

        # if the lecturer performance process is successful
        if lecturer_batch_process_response:

            # start the batch processing for monitoring student behavior component
            student_batch_process_response = student_behavior_batch_process(student_video_id, student_video_name)

            # if the student behavior process is successful
            if student_batch_process_response:
                is_all_processed = True


    # return the status
    return is_all_processed


# test the above method using 'main' method
# if __name__ == '__main__':
#
#     lecturer = 1
#     subject = 16
#     subject_code = "IT1120"
#
#     # call the method
#     automation_process(lecturer, subject, subject_code)
