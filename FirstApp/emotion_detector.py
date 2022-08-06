"""

this file contain the relevant methods to implement the student emotion recognition logic

main methods include
    * the execution of emotion recognition model and saving the results into the database,
    * retrieving the emotion recognition details for lectures within a given time period
    * calculating the emotion recognition details for each frame, for a given lecture
    * calculating the emotion recognition details for frame groups, for a given lecture
    * calculating the emotion recognition correlations with the lecturer posture activities



"""


from tensorflow.keras.models import load_model
from keras.preprocessing.image import img_to_array
import cv2
import os
import numpy as np

from .MongoModels import *
from . models import VideoMeta
from . logic import custom_sorter as cs
from .logic import id_generator as ig
from .logic import activity_recognition as ar
from .logic import utilities as ut
from .serializers import LectureEmotionSerializer

import pandas as pd

# emotion recognition method
# this method accepts:
#     classifier: emotion recognition classifier (VGG model)
#     face_classifier: face detection classifier (Haar-Cascade)
#     image: image to be processed

# returns:
#     label: the emotion recognition label

def emotion_recognition(classifier, face_classifier, image):
    # this label will contain the recognized emotion label
    label = ""
    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # the detected faces in the image
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
        # rect,face,image = face_detector(frame)
        # draw a rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype('float') / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            # make a prediction on the ROI, then lookup the class

            preds = classifier.predict(roi)[0]
            label = class_labels[preds.argmax()]

            # put the emotion label
            cv2.putText(image, label, (x, y), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)

    return label


# this method will perform emotion recognition for a lecture
# this method accepts:
#     video_path: the lecture video name

# returns:
#     percentages: the student activity percentages for the lecture video

def detect_emotion(video):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video))
    face_classifier = cv2.CascadeClassifier(os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)
    EMOTION_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\emotion")
    meta_data = VideoMeta()

    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']


    cap = cv2.VideoCapture(VIDEO_DIR)
    fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    #taking a count on each label
    count_frames = 0
    count_angry = 0
    count_happy = 0
    count_sad = 0
    count_neutral = 0
    count_surprise = 0

    # for testing purposes
    print('starting the emotion recognition process')

    # get width and height of the video frames
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # get the video frame size
    size = (frame_width, frame_height)

    # this is the annotated video path
    ANNOTATED_VIDEO_PATH = os.path.join(EMOTION_DIR, video)

    # initiailizing the video writer
    vid_cod = cv2.VideoWriter_fourcc(*'XVID')
    output = cv2.VideoWriter(ANNOTATED_VIDEO_PATH, vid_cod, 30.0, size)

    while (count_frames < frame_count):
        # Grab a single frame of video
        ret, frame = cap.read()
        labels = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray,1.3,5)

        label = emotion_recognition(classifier, face_classifier, frame)

        # counting the number of frames for each label, to calculate the percentage for each emotion later on...

        if (label == 'Anger'):
            count_angry += 1
            # path = os.path.join(BASE_DIR, 'static\\images\\Anger')
            # cv2.imwrite(os.path.join(path, 'Anger-{0}.jpg'.format(count)), frame)

        elif (label == 'Happy'):
            count_happy += 1
            # path = os.path.join(BASE_DIR, 'static\\images\\Happy')
            # cv2.imwrite(os.path.join(path, 'Happy-{0}.jpg'.format(count)), frame)

        elif (label == 'Neutral'):
            count_neutral += 1
            # path = os.path.join(BASE_DIR, 'static\\images\\Neutral')
            # cv2.imwrite(os.path.join(path, 'Neutral-{0}.jpg'.format(count)), frame)

        elif (label == 'Sad'):
            count_sad += 1

        elif (label == 'Surprise'):
            count_surprise += 1


        # for testing purposes
        print('emotion frame count: ', count_frames)

        # write the video frame to the video writer
        output.write(frame)

        count_frames += 1

    # setting up the counted values
    meta_data.frame_count = count_frames
    meta_data.happy_count = count_happy
    meta_data.sad_count = count_sad
    meta_data.angry_count = count_angry
    meta_data.neutral_count = count_neutral
    meta_data.surprise_count = count_surprise

    cap.release()
    output.release()
    cv2.destroyAllWindows()

    # after saving the video, save the changes to static content
    p = os.popen("python manage.py collectstatic", "w")
    p.write("yes")

    # for testing purposes
    print('ending the emotion recognition process')

    # return the data
    return meta_data



# this method will recognize the student emotions for each frame
# this method will accept:
#     video_name: the lecture video name

# returns:
#     sorted_emotion_frame_recognitions: the list of sorted student emotion recognitions for each frame

def get_frame_emotion_recognition(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))
    face_classifier = cv2.CascadeClassifier(
        os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)

    # files required for person detection
    config_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.prototxt.txt")
    model_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.caffemodel")

    # load our serialized persosn detection model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(config_file, model_file)


    cap = cv2.VideoCapture(VIDEO_DIR)
    no_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    # initializing the count variables
    frame_count = 0


    # frame activity recognitions
    frame_emotion_recognitions = []

    # # class labels
    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']


    # for testing purposes
    print('starting the emotion frame recognition process')



    # looping through the frames
    while (frame_count < no_of_frames):

        ret, image = cap.read()

        frame_name = "frame-{}".format(frame_count)

        frame_details = {}
        frame_details['frame_name'] = frame_name

        # initialize the count variables for a frame
        happy_count = 0
        sad_count = 0
        angry_count = 0
        neutral_count = 0
        surprise_count = 0

        # get the detections
        detections, persons = ar.person_detection(image, net)

        # to count the extracted detections for a frame
        detection_count = 0

        # if there are detections
        if (len(detections) > 0):

            # loop through the detections
            for person in persons:


                label = emotion_recognition(classifier, face_classifier, person)

                # checking for the label
                if label == class_labels[0]:
                    angry_count += 1
                elif label == class_labels[1]:
                    happy_count += 1
                elif label == class_labels[2]:
                    neutral_count += 1
                elif label == class_labels[3]:
                    sad_count += 1
                elif label == class_labels[4]:
                    surprise_count += 1

                # increment the detection count
                detection_count += 1



            # calculating the percentages for the frame
            happy_perct = float(happy_count / detection_count) * 100 if detection_count > 0 else 0
            sad_perct = float(sad_count / detection_count) * 100 if detection_count > 0 else 0
            angry_perct = float(angry_count / detection_count) * 100 if detection_count > 0 else 0
            neutral_perct = float(neutral_count / detection_count) * 100 if detection_count > 0 else 0
            surprise_perct = float(surprise_count / detection_count) * 100 if detection_count > 0 else 0

            # this dictionary will be returned
            frame_details['happy_perct'] = happy_perct
            frame_details['sad_perct'] = sad_perct
            frame_details['angry_perct'] = angry_perct
            frame_details['neutral_perct'] = neutral_perct
            frame_details['surprise_perct'] = surprise_perct

            # push to all the frame details
            frame_emotion_recognitions.append(frame_details)

        else:
            break


        # for testing purposes
        print('emotion frame recognition count: ', frame_count)

        # increment the frame count
        frame_count += 1

    # sort the recognitions based on the frame number
    sorted_emotion_frame_recognitions = cs.custom_object_sorter(frame_emotion_recognitions)


    # for testing purposes
    print('ending the emotion frame recognition process')

    # return the detected frame percentages
    return sorted_emotion_frame_recognitions


# this method will get the student emotion  recognition summary for period
# this method accepts the following parameter
# emotions: the database records retrieved within the given time period

# returns:
#     percentages: average percentages for each student activity recognition label
#     individual_lec_emotions: contain the lecture emotion recognition details for each individual lecture
#     emotion_labels: the emotion labels

def get_student_emotion_summary_for_period(emotions):

    # declare variables to add percentage values
    happy_perct_combined = 0.0
    sad_perct_combined = 0.0
    angry_perct_combined = 0.0
    disgust_perct_combined = 0.0
    surprise_perct_combined = 0.0
    neutral_perct_combined = 0.0

    # get the number of activties to calculate average
    no_of_emotions = len(emotions)

    # this list will contain the emotion recognition details for each lecture
    individual_lec_emotions = []

    # emotion labels
    emotion_labels = ["happy_perct", "sad_perct", "angry_perct", "disgust_perct", "surprise_perct", "neutral_perct"]

    # iterate through the activities
    for emotion in emotions:

        individual_emotion = {}
        individual_emotion["happy_perct"] = float(emotion['happy_perct'])
        individual_emotion["sad_perct"] = float(emotion['sad_perct'])
        individual_emotion["angry_perct"] = float(emotion['angry_perct'])
        individual_emotion["disgust_perct"] = float(emotion['disgust_perct'])
        individual_emotion["surprise_perct"] = float(emotion['surprise_perct'])
        individual_emotion["neutral_perct"] = float(emotion['neutral_perct'])

        happy_perct_combined += float(emotion['happy_perct'])
        sad_perct_combined += float(emotion['sad_perct'])
        angry_perct_combined += float(emotion['angry_perct'])
        disgust_perct_combined += float(emotion['disgust_perct'])
        surprise_perct_combined += float(emotion['surprise_perct'])
        neutral_perct_combined += float(emotion['neutral_perct'])

        # append to the list
        individual_lec_emotions.append(individual_emotion)


    # calculate the average percentages
    happy_average_perct = round((happy_perct_combined / no_of_emotions), 1)
    sad_average_perct = round((sad_perct_combined / no_of_emotions), 1)
    angry_average_perct = round((angry_perct_combined / no_of_emotions), 1)
    disgust_average_perct = round((disgust_perct_combined / no_of_emotions), 1)
    surprise_average_perct = round((surprise_perct_combined / no_of_emotions), 1)
    neutral_average_perct = round((neutral_perct_combined / no_of_emotions), 1)

    # this dictionary will contain the student emotion average percentage values
    percentages = {}
    percentages["happy_perct"] = happy_average_perct
    percentages["sad_perct"] = sad_average_perct
    percentages["angry_perct"] = angry_average_perct
    percentages["disgust_perct"] = disgust_average_perct
    percentages["surprise_perct"] = surprise_average_perct
    percentages["neutral_perct"] = neutral_average_perct

    # return the values
    return percentages, individual_lec_emotions, emotion_labels


# this method will get the lecture student emotion frame groupings
# this method accepts:
#     video_name: the lecture video name
#     frame_landmarks: the specific frames in the extracted set of frames from the lecture video
#     frame_group_dict: the dictionary which contains the frame groups and the relevant student emotion labels for each frame group

# returns:
#     frame_group_dict: the modified frame group dictionary
#     emotion_labels: student emotion labels

def emotion_frame_groupings(video_name, frame_landmarks, frame_group_dict):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))
    face_classifier = cv2.CascadeClassifier(
        os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)

    # files required for person detection
    config_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.prototxt.txt")
    model_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.caffemodel")

    # load our serialized persosn detection model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(config_file, model_file)

    # capture the video
    cap = cv2.VideoCapture(VIDEO_DIR)
    no_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    # initializing the count variables
    frame_count = 0

    # class labels
    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    # get the frame differences for each frame group
    frame_group_diff = {}

    # loop through the frame group dictionary
    for key in frame_group_dict.keys():
        split_values = key.split("-")
        value1 = int(split_values[0])
        value2 = int(split_values[1])
        diff = value2 - value1

        # assign the difference
        frame_group_diff[key] = diff if diff > 0 else 1


    # looping through the frames
    while (frame_count < no_of_frames):

        # get the current frame
        ret, image = cap.read()


        # initializing the variables
        happy_count = 0
        sad_count = 0
        angry_count = 0
        surprise_count = 0
        neutral_count = 0
        detection_count = 0

        detections, persons = ar.person_detection(image, net)

        # if there are detections
        if (len(detections) > 0):

            # looping through the detections in each frame
            for person in persons:


                # run the model and get the emotion label
                label = emotion_recognition(classifier, face_classifier, person)

                # increment the count based on the label
                if label == class_labels[0]:
                    angry_count += 1
                if label == class_labels[1]:
                    happy_count += 1
                if label == class_labels[2]:
                    neutral_count += 1
                if label == class_labels[3]:
                    sad_count += 1
                if label == class_labels[4]:
                    surprise_count += 1


                # increment the detection count
                detection_count += 1


                # finding the time landmark that the current frame is in
                for i in frame_landmarks:
                    index = frame_landmarks.index(i)
                    j = index + 1

                    # checking whether the next index is within the range
                    if j < len(frame_landmarks):
                        next_value = frame_landmarks[j]

                        # checking the correct time landmark range
                        if (frame_count >= i) & (frame_count < next_value):
                            frame_name = "{}-{}".format(i, next_value)


                            frame_group_dict[frame_name]['happy_count'] += happy_count
                            frame_group_dict[frame_name]['sad_count'] += sad_count
                            frame_group_dict[frame_name]['angry_count'] += angry_count
                            frame_group_dict[frame_name]['surprise_count'] += surprise_count
                            frame_group_dict[frame_name]['neutral_count'] += neutral_count
                            frame_group_dict[frame_name]['detection_count'] += detection_count

        else:
            break

        # for testing purposes
        print('emotion frame groupings count: ', frame_count)

        # increment the frame count
        frame_count += 1

    # calculate the percentage values
    for key in frame_group_dict.keys():
        frame_group_details = frame_group_dict[key]
        frame_group_happy_count = frame_group_details['happy_count']
        frame_group_sad_count = frame_group_details['sad_count']
        frame_group_angry_count = frame_group_details['angry_count']
        frame_group_surprise_count = frame_group_details['surprise_count']
        frame_group_neutral_count = frame_group_details['neutral_count']
        group_detection_count = frame_group_details['detection_count']

        # calculate the frame group emotion percentages
        frame_group_happy_perct = float(frame_group_happy_count / group_detection_count) * 100 if group_detection_count > 0 else 0
        frame_group_sad_perct = float(frame_group_sad_count / group_detection_count) * 100 if group_detection_count > 0 else 0
        frame_group_angry_perct = float(frame_group_angry_count / group_detection_count) * 100 if group_detection_count > 0 else 0
        frame_group_surprise_perct = float(frame_group_surprise_count / group_detection_count) * 100 if group_detection_count > 0 else 0
        frame_group_neutral_perct = float(frame_group_neutral_count / group_detection_count) * 100 if group_detection_count > 0 else 0

        # assign the values to the same dictionary
        frame_group_dict[key]['happy_perct'] = round(frame_group_happy_perct, 1)
        frame_group_dict[key]['sad_perct'] = round(frame_group_sad_perct, 1)
        frame_group_dict[key]['angry_perct'] = round(frame_group_angry_perct, 1)
        frame_group_dict[key]['surprise_perct'] = round(frame_group_surprise_perct, 1)
        frame_group_dict[key]['neutral_perct'] = round(frame_group_neutral_perct, 1)

        # removing irrelevant items from the dictionary
        frame_group_dict[key].pop('happy_count')
        frame_group_dict[key].pop('sad_count')
        frame_group_dict[key].pop('angry_count')
        frame_group_dict[key].pop('surprise_count')
        frame_group_dict[key].pop('neutral_count')
        frame_group_dict[key].pop('detection_count')

    # print('frame group dict: ', frame_group_dict)
    emotion_labels = ['happy_perct', 'sad_perct', 'angry_perct', 'surprise_perct', 'neutral_perct']


    # return the dictionary
    return frame_group_dict, emotion_labels


# THIS SECTION WILL HANDLE SOME DATABASE OPERATIONS

# this method will save frame detections to the database
# this method will accept
#     video_name: lecture video name to be processed

# returns
#     frame_detections: the student emotion frame detections

def save_frame_recognitions(video_name):

    # for testing purposes
    print('starting the saving emotion frame recognition process')

    # retrieve the lecture emotion id
    lec_emotion = LectureEmotionReport.objects.filter(lecture_video_id__video_name=video_name)
    lec_emotion_ser = LectureEmotionSerializer(lec_emotion, many=True)
    lec_emotion_data = lec_emotion_ser.data[0]
    lec_emotion_id = lec_emotion_data['id']

    # create a new lecture activity frame detections id
    last_lec_emotion_frame_recognitions = LectureEmotionFrameRecognitions.objects.order_by(
        'lecture_emotion_frame_recognition_id').last()
    new_lecture_emotion_frame_recognitions_id = "LEFR00001" if (
            last_lec_emotion_frame_recognitions is None) else \
        ig.generate_new_id(last_lec_emotion_frame_recognitions.lecture_emotion_frame_recognition_id)

    # calculate the frame detections
    frame_detections = get_frame_emotion_recognition(video_name)

    frame_recognition_details = []

    # save the new lecture activity frame recognitions
    for detection in frame_detections:
        lec_emotion_frame_recognition_details = LectureEmotionFrameRecognitionDetails()
        lec_emotion_frame_recognition_details.frame_name = detection['frame_name']
        lec_emotion_frame_recognition_details.happy_perct = detection['happy_perct']
        lec_emotion_frame_recognition_details.sad_perct = detection['sad_perct']
        lec_emotion_frame_recognition_details.angry_perct = detection['angry_perct']
        lec_emotion_frame_recognition_details.surprise_perct = detection['surprise_perct']
        lec_emotion_frame_recognition_details.neutral_perct = detection['neutral_perct']

        frame_recognition_details.append(lec_emotion_frame_recognition_details)

    lec_emotion_frame_recognitions = LectureEmotionFrameRecognitions()
    lec_emotion_frame_recognitions.lecture_emotion_frame_recognition_id = new_lecture_emotion_frame_recognitions_id
    lec_emotion_frame_recognitions.lecture_emotion_id_id = lec_emotion_id
    lec_emotion_frame_recognitions.frame_recognition_details = frame_recognition_details

    lec_emotion_frame_recognitions.save()

    # for testing purposes
    print('ending the saving emotion frame recognition process')

    # now return the frame recognitions
    return frame_detections


# this method will save gaze frame groupings to the database
# this method accepts:
#     video_name: the lecture video name
#     frame_landmarks: the specific frames in the extracted set of frames from the lecture video
#     frame_group_dict: the dictionary which contains the frame groups and the relevant student emotion labels for each frame group

def save_frame_groupings(video_name, frame_landmarks, frame_group_dict):

    # for testing purposes
    print('starting the saving emotion frame grouoings process')

    frame_group_percentages, emotion_labels = emotion_frame_groupings(video_name, frame_landmarks, frame_group_dict)

    # save the frame group details into db
    last_lec_emotion_frame_grouping = LectureEmotionFrameGroupings.objects.order_by('lecture_emotion_frame_groupings_id').last()
    new_lecture_emotion_frame_grouping_id = "LEFG00001" if (last_lec_emotion_frame_grouping is None) else \
        ig.generate_new_id(last_lec_emotion_frame_grouping.lecture_emotion_frame_groupings_id)

    # retrieve the lecture emotion id
    lec_emotion = LectureEmotionReport.objects.filter(lecture_video_id__video_name=video_name)
    lec_emotion_ser = LectureEmotionSerializer(lec_emotion, many=True)
    lec_emotion_id = lec_emotion_ser.data[0]['id']

    # create the frame group details
    frame_group_details = []

    for key in frame_group_percentages.keys():
        # create an object of type 'LectureActivityFrameGroupDetails'
        lec_emotion_frame_group_details = LectureEmotionFrameGroupDetails()
        lec_emotion_frame_group_details.frame_group = key
        lec_emotion_frame_group_details.frame_group_percentages = frame_group_percentages[key]

        frame_group_details.append(lec_emotion_frame_group_details)


    new_lec_emotion_frame_groupings = LectureEmotionFrameGroupings()
    new_lec_emotion_frame_groupings.lecture_emotion_frame_groupings_id = new_lecture_emotion_frame_grouping_id
    new_lec_emotion_frame_groupings.lecture_emotion_id_id = lec_emotion_id
    new_lec_emotion_frame_groupings.frame_group_details = frame_group_details

    # for testing purposes
    print('ending the saving emotion frame groupings process')

    # save
    new_lec_emotion_frame_groupings.save()



# this method will get student emotion correlations
# this method accepts:
#     individual_lec_emotions: the student emotion details for each individual lecture
#     lec_recorded_activity_data: the lecturer posture recognition details

# returns:
#     correlations: the lecture student emotions and lecturer posture recognition correlations

def get_emotion_correlations(individual_lec_emotions, lec_recorded_activity_data):
    # this variable will be used to store the correlations
    correlations = []

    # limit = 10
    limit = len(individual_lec_emotions)

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(individual_lec_emotions))]

    # declare the correlation data dictionary
    corr_data = {}

    # student activity labels
    student_emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprise', 'Neutral']
    lecturer_activity_labels = ['seated', 'standing', 'walking']

    # lecturer recorded data list (lecturer)
    sitting_perct_list = []
    standing_perct_list = []
    walking_perct_list = []

    # lecture activity data list (student)
    happy_perct_list = []
    sad_perct_list = []
    angry_perct_list = []
    surprise_perct_list = []
    neutral_perct_list = []


    # loop through the lecturer recorded data (lecturer)
    for data in lec_recorded_activity_data:
        value = int(data['seated_count'])
        value1 = int(data['standing_count'])
        value2 = int(data['walking_count'])

        if value != 0:
            sitting_perct_list.append(int(data['seated_count']))
        if value1 != 0:
            standing_perct_list.append(int(data['standing_count']))
        if value2 != 0:
            walking_perct_list.append(int(data['walking_count']))

    # loop through the lecturer recorded data (student)
    for data in individual_lec_emotions:
        value = int(data['happy_perct'])
        value1 = int(data['sad_perct'])
        value2 = int(data['angry_perct'])
        value3 = int(data['surprise_perct'])
        value4 = int(data['neutral_perct'])

        if value != 0:
            happy_perct_list.append(int(data['happy_perct']))
        if value1 != 0:
            sad_perct_list.append(int(data['sad_perct']))
        if value2 != 0:
            angry_perct_list.append(int(data['angry_perct']))
        if value3 != 0:
            surprise_perct_list.append(int(data['surprise_perct']))
        if value4 != 0:
            neutral_perct_list.append(int(data['neutral_perct']))


    if len(happy_perct_list) == len(individual_lec_emotions):
        corr_data[student_emotion_labels[0]] = happy_perct_list
    if len(sad_perct_list) == len(individual_lec_emotions):
        corr_data[student_emotion_labels[1]] = sad_perct_list
    if len(angry_perct_list) == len(individual_lec_emotions):
        corr_data[student_emotion_labels[2]] = angry_perct_list
    if len(surprise_perct_list) == len(individual_lec_emotions):
        corr_data[student_emotion_labels[3]] = surprise_perct_list
    if len(neutral_perct_list) == len(individual_lec_emotions):
        corr_data[student_emotion_labels[4]] = neutral_perct_list
    if (len(sitting_perct_list)) == len(individual_lec_emotions):
        corr_data[lecturer_activity_labels[0]] = sitting_perct_list
    if (len(standing_perct_list)) == len(individual_lec_emotions):
        corr_data[lecturer_activity_labels[1]] = standing_perct_list
    if (len(walking_perct_list)) == len(individual_lec_emotions):
        corr_data[lecturer_activity_labels[2]] = walking_perct_list


    # corr_data = {'Happy': happy_perct_list, 'Sad': sad_perct_list, 'Angry': angry_perct_list, 'Surprise': surprise_perct_list, 'Neutral': neutral_perct_list,
    #              'seated': sitting_perct_list, 'standing': standing_perct_list, 'walking': walking_perct_list}

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    print(df)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

    print('====correlated variables=====')
    print(pd_series)

    # assign a new value to the 'limit' variable
    limit = len(pd_series) if len(pd_series) < limit else limit

    for i in range(limit):
        # this dictionary will get the pandas.Series object's  indices and values separately
        corr_dict = {}

        index = pd_series.index[i]

        # check whether the first index is a student activity
        isStudentEmotion = index[0] in student_emotion_labels
        # check whether the second index is a lecturer activity
        isLecturerAct = index[1] in lecturer_activity_labels

        # if both are student and lecturer activities, add to the dictionary
        if isStudentEmotion & isLecturerAct:
            corr_dict['index'] = index
            corr_dict['value'] = pd_series.values[i]

            # append the dictionary to the 'correlations' list
            correlations.append(corr_dict)

    # return the list
    return correlations
