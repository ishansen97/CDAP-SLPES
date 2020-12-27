import os
import cv2
import shutil
# import datetime
from datetime import timedelta

from FirstApp.MongoModels import *
from FirstApp.serializers import *
from . import id_generator as ig


def VideoExtractor(request):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    video_name = request["video_name"]

    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos")
    VIDEO_PATH = os.path.join(VIDEO_DIR, video_name)

    # creating the new path to store extracted frames
    NEW_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\extracted\\{}".format(video_name))

    # check whether a specific directory exists
    if (os.path.isdir(NEW_DIR)):
        shutil.rmtree(NEW_DIR)

    # create the new directory
    os.mkdir(NEW_DIR)

    video = cv2.VideoCapture(VIDEO_PATH)

    no_of_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0


    while (frame_count < no_of_frames):

        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        new_file_name = "{}_frame_{}.png".format(video_name, frame_count)
        new_file_path = os.path.join(NEW_DIR, new_file_name)

        # save the extracted frames
        cv2.imwrite(new_file_path, gray)

        frame_count += 1


    # after extracting the frames, save the changes to static content
    p = os.popen("python manage.py collectstatic", "w")
    p.write("yes")

# retrieving the extracted frames for a given video
def getExtractedFrames(request):

    folder_name = request.get("folder_name")
    image_list = []

    print('folder name: ', folder_name)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\extracted\\{}".format(folder_name))

    # listing all the images in the directory
    for image in os.listdir(EXTRACTED_DIR):
        image_details = {"image": image}
        image_list.append(image_details)



    # checking for the number of frames
    if (len(image_list) > 0):
        return image_list

    else:
        return "No extracted frames were found"


# this method will retrieve the time landmarks for a lecture video
def getTimeLandmarks(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))

    # iteration
    video = cv2.VideoCapture(VIDEO_PATH)
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_count = 0

    # calculating the duration in seconds
    duration = int(no_of_frames / fps)

    # define the number of time gaps required
    THRESHOLD_GAP = 5

    # calculating the real duration
    real_duration = timedelta(seconds=(duration))

    # defines the number of seconds included for a frame group
    THRESHOLD_TIME = 10


    # define an unit gap
    unit_gap = int(duration / THRESHOLD_GAP)

    initial_landmark = 0

    # time_landmarks = ['0:00:00']
    time_landmarks = []
    time_landmarks_values = [0]

    # loop through the threshold gap limit to define the time landmarks
    for i in range(THRESHOLD_GAP):
        initial_landmark += unit_gap
        time_landmark = str(timedelta(seconds=initial_landmark))
        time_landmark_value = initial_landmark
        time_landmarks.append(time_landmark)
        time_landmarks_values.append(time_landmark_value)

    # append the final time
    time_landmarks.append(str(real_duration))
    time_landmarks_values.append(duration)

    return time_landmarks


# this method will retrieve the time landmarks for a lecture video
def getFrameLandmarks(video_name, category):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))

    # iteration
    video = cv2.VideoCapture(VIDEO_PATH)
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    int_no_of_frames = int(no_of_frames)
    fps = int(video.get(cv2.CAP_PROP_FPS))

    # list of categories
    categories = ["Activity", "Emotion", "Gaze"]

    # define the number of time gaps required
    THRESHOLD_GAP = 5

    # define a frame gap
    frame_gap = int(int_no_of_frames / THRESHOLD_GAP)

    initial_frame_landmark = 0

    # define frame landmarks
    frame_landmarks = [0]
    # frame_landmarks = []

    # loop through the threshold gap limit to define the time landmarks
    for i in range(THRESHOLD_GAP):
        initial_frame_landmark += frame_gap

        frame_landmarks.append(initial_frame_landmark)

    # append the final frame
    frame_landmarks.append(int_no_of_frames)

    # defining the frame group dictionary
    frame_group_list = []

    # creating frame group names
    for landmark in frame_landmarks:
        index = frame_landmarks.index(landmark)
        j = index + 1

        # if the next index is within the range of the list
        if j < len(frame_landmarks):
            next_value = frame_landmarks[j]

            group_name = "{}-{}".format(landmark, next_value)

            # append to the list
            frame_group_list.append(group_name)


    # define a dictionary to hold the frame groups
    frame_group_dict = {}

    # checking for the category
    if category == categories[0]:
        # loop through the group names to create a dictionary
        for name in frame_group_list:
            frame_group_dict[name] = {'phone_count': 0, 'listen_count': 0, 'note_count': 0, 'detection_count': 0}

    elif category == categories[1]:
        # loop through the group names to create a dictionary
        for name in frame_group_list:
            frame_group_dict[name] = {'happy_count': 0, 'sad_count': 0, 'angry_count': 0, 'surprise_count': 0, 'neutral_count': 0, 'detection_count': 0}

    elif category == categories[2]:
        # loop through the group names to create a dictionary
        for name in frame_group_list:
            frame_group_dict[name] = {'upright_count': 0, 'upleft_count': 0, 'downright_count': 0, 'downleft_count': 0,
                                      'front_count': 0, 'detection_count': 0}

    return frame_landmarks, frame_group_dict



# this section will handle some database operations
def save_time_landmarks(video_name):

    # for testing purposes
    print('starting the saving time landmarks process')

    last_lec_video_time_landmarks = LectureVideoTimeLandmarks.objects.order_by('lecture_video_time_landmarks_id').last()
    new_lecture_video_time_landmarks_id = "LVTL00001" if (last_lec_video_time_landmarks is None) else \
            ig.generate_new_id(last_lec_video_time_landmarks.lecture_video_time_landmarks_id)


    # retrieve lecture video details
    lec_video = LectureVideo.objects.filter(video_name=video_name)
    lec_video_ser = LectureVideoSerializer(lec_video, many=True)
    lec_video_id = lec_video_ser.data[0]['id']


    # save the landmark details in the db
    time_landmarks = getTimeLandmarks(video_name)

    db_time_landmarks = []

    # loop through the time landmarks
    for landmark in time_landmarks:
        landmark_obj = Landmarks()
        landmark_obj.landmark = landmark

        db_time_landmarks.append(landmark_obj)


    new_lec_video_time_landmarks = LectureVideoTimeLandmarks()
    new_lec_video_time_landmarks.lecture_video_time_landmarks_id = new_lecture_video_time_landmarks_id
    new_lec_video_time_landmarks.lecture_video_id_id = lec_video_id
    new_lec_video_time_landmarks.time_landmarks = db_time_landmarks

    # for testing purposes
    print('ending the saving time landmarks process')

    new_lec_video_time_landmarks.save()


# this method will save frame landmarks to the database
def save_frame_landmarks(video_name):

    # for testing purposes
    print('starting the saving frame landmarks process')

    # retrieve the previous lecture video frame landmarks details
    last_lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.order_by(
        'lecture_video_frame_landmarks_id').last()
    new_lecture_video_frame_landmarks_id = "LVFL00001" if (last_lec_video_frame_landmarks is None) else \
        ig.generate_new_id(last_lec_video_frame_landmarks.lecture_video_frame_landmarks_id)

    frame_landmarks, frame_group_dict = getFrameLandmarks(video_name, "Activity")


    # retrieve lecture video details
    lec_video = LectureVideo.objects.filter(video_name=video_name)
    lec_video_ser = LectureVideoSerializer(lec_video, many=True)
    lec_video_id = lec_video_ser.data[0]['id']


    # save the frame landmarks details into db
    db_frame_landmarks = []

    for landmark in frame_landmarks:
        landmark_obj = Landmarks()
        landmark_obj.landmark = landmark

        db_frame_landmarks.append(landmark_obj)


    new_lec_video_frame_landmarks = LectureVideoFrameLandmarks()
    new_lec_video_frame_landmarks.lecture_video_frame_landmarks_id = new_lecture_video_frame_landmarks_id
    new_lec_video_frame_landmarks.lecture_video_id_id = lec_video_id
    new_lec_video_frame_landmarks.frame_landmarks = db_frame_landmarks

    new_lec_video_frame_landmarks.save()

    # for testing purposes
    print('ending the saving frame landmarks process')

    # now return the frame landmarks and the frame group dictionary
    return frame_landmarks, frame_group_dict


# this method will retrieve the frame landmarks from the database
def get_frame_landmarks(video_name):

    frame_landmarks = []

    # retrieve frame landmarks from db
    lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.filter(lecture_video_id__video_name=video_name)
    lec_video_frame_landmarks_ser = LectureVideoFrameLandmarksSerializer(lec_video_frame_landmarks, many=True)
    lec_video_frame_landmarks_data = lec_video_frame_landmarks_ser.data[0]

    retrieved_frame_landmarks = lec_video_frame_landmarks_data["frame_landmarks"]

    # creating a new list to display in the frontend
    for landmark in retrieved_frame_landmarks:
        frame_landmarks.append(landmark['landmark'])


    # now return the frame landmarks
    return frame_landmarks


# this method will save leture video (student)
def save_lecture_student_video():
    pass