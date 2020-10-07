import os
import cv2
import shutil
import datetime

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
    real_duration = datetime.timedelta(seconds=(duration+THRESHOLD_GAP))

    # defines the number of seconds included for a frame group
    THRESHOLD_TIME = 10


    # define an unit gap
    unit_gap = int(duration / THRESHOLD_GAP)

    initial_landmark = 0

    time_landmarks = ['0:00:00']
    time_landmarks_values = [0]

    # loop through the threshold gap limit to define the time landmarks
    for i in range(THRESHOLD_GAP):
        initial_landmark += unit_gap
        time_landmark = str(datetime.timedelta(seconds=initial_landmark))
        time_landmark_value = initial_landmark
        time_landmarks.append(time_landmark)
        time_landmarks_values.append(time_landmark_value)

    # append the final time
    time_landmarks.append(str(real_duration))
    time_landmarks_values.append(duration)

    return time_landmarks


# this method will retrieve the time landmarks for a lecture video
def getFrameLandmarks(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))

    # iteration
    video = cv2.VideoCapture(VIDEO_PATH)
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    int_no_of_frames = int(no_of_frames)
    fps = int(video.get(cv2.CAP_PROP_FPS))

    # calculating the duration in seconds
    duration = int(no_of_frames / fps)

    # define the number of time gaps required
    THRESHOLD_GAP = 5

    # define a frame gap
    frame_gap = int(int_no_of_frames / THRESHOLD_GAP)

    initial_frame_landmark = 0

    # define frame landmarks
    frame_landmarks = [0]

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

    # loop through the group names to create a dictionary
    for name in frame_group_list:
        frame_group_dict[name] = {'phone_count': 0, 'listen_count': 0, 'note_count': 0}


    return frame_landmarks, frame_group_dict