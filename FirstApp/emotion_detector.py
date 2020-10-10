from tensorflow.keras.models import load_model
from time import sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image
import cv2
import os
import numpy as np
from . models import VideoMeta
from . logic import custom_sorter as cs


# emotion recognition method
def emotion_recognition(classifier, face_classifier, image):
    label = ""
    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
        # rect,face,image = face_detector(frame)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype('float') / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            # make a prediction on the ROI, then lookup the class

            preds = classifier.predict(roi)[0]
            label = class_labels[preds.argmax()]

    return label


def detect_emotion(video):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video))
    face_classifier = cv2.CascadeClassifier(os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)
    path = ''
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

    while (count_frames < frame_count):
        # Grab a single frame of video
        ret, frame = cap.read()
        labels = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray,1.3,5)


        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
        # rect,face,image = face_detector(frame)


            if np.sum([roi_gray])!=0:
                roi = roi_gray.astype('float')/255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

            # make a prediction on the ROI, then lookup the class

                preds = classifier.predict(roi)[0]
                label = class_labels[preds.argmax()]

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

                label_position = (x, y)
                # cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                # cv2.imwrite("".format(label, count), frame)
            else:
                cv2.putText(frame, 'No Face Found', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        count_frames += 1

    # setting up the counted values
    meta_data.frame_count = count_frames
    meta_data.happy_count = count_happy
    meta_data.sad_count = count_sad
    meta_data.angry_count = count_angry
    meta_data.neutral_count = count_neutral
    meta_data.surprise_count = count_surprise

    cap.release()
    cv2.destroyAllWindows()

    return meta_data


# to retrieve student evaluation for emotions
def get_student_emotion_evaluations(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # face_classifier = cv2.CascadeClassifier(
    #     os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    # classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    # classifier = load_model(classifier_path)
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))

    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    detections = []
    frames = []

    for frame_folder in os.listdir(EXTRACTED_DIR):

        FRAME_DIR = os.path.join(EXTRACTED_DIR, frame_folder)
        frame_details = {}
        frame_details['frame'] = frame_folder

        # for each detection in the frame directory
        detected_images = []
        for detection in os.listdir(FRAME_DIR):

            if "frame" not in detection:
                DETECTION_PATH = os.path.join(FRAME_DIR, detection)

                image = cv2.imread(DETECTION_PATH)

                # label = emotion_recognition(classifier, face_classifier, image)

                detected_images.append(detection)
                detections.append(detection)

        frame_details['detections'] = detected_images
        frames.append(frame_details)

    sorted_frames = cs.custom_object_sorter(frames)
    set_detections = set(detections)
    list_set_detections = list(set_detections)

    sorted_list_set_detections = cs.custom_sort(list_set_detections)

    return sorted_frames, sorted_list_set_detections


# this method will retrieve individual student evaluations
def get_individual_student_evaluation(video_name, student_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    face_classifier = cv2.CascadeClassifier(
        os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))

    # the object of type 'VideoMeta'
    meta_data = VideoMeta()

    # the class labels
    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    # taking a count on each label
    count_frames = 0
    count_angry = 0
    count_happy = 0
    count_sad = 0
    count_neutral = 0
    count_surprise = 0

    for frame in os.listdir(EXTRACTED_DIR):
        # getting the frame folder
        FRAME_FOLDER = os.path.join(EXTRACTED_DIR, frame)

        for detections in os.listdir(FRAME_FOLDER):

            # only take the images with the student name
            if detections == student_name:
                # get the label for this image
                IMAGE_PATH = os.path.join(FRAME_FOLDER, detections)
                image = cv2.imread(IMAGE_PATH)

                label = emotion_recognition(classifier, face_classifier, image)

                # check for the label of the image
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
                    # path = os.path.join(BASE_DIR, 'static\\images\\Sad')
                    # cv2.imwrite(os.path.join(path, 'Sad-{0}.jpg'.format(count)), frame)

                elif (label == 'Surprise'):
                    count_surprise += 1
                    # path = os.path.join(BASE_DIR, 'static\\images\\Surprise')
                    # cv2.imwrite(os.path.join(path, 'Surprise-{0}.jpg'.format(count)), frame)

        # incrementing the frame_count
        count_frames += 1
    # setting up the counted values

    meta_data.frame_count = count_frames
    meta_data.happy_count = count_happy
    meta_data.sad_count = count_sad
    meta_data.angry_count = count_angry
    meta_data.neutral_count = count_neutral
    meta_data.surprise_count = count_surprise

    # calculating the percentages
    meta_data.calcPercentages()

    return meta_data

# this method will
def get_frame_emotion_recognition(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    face_classifier = cv2.CascadeClassifier(
        os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))

    # initializing the count variables
    frame_count = 0


    # frame activity recognitions
    frame_emotion_recognitions = []


    # # class labels
    class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']

    for frame in os.listdir(EXTRACTED_DIR):
        # derive the frame folder path
        FRAME_FOLDER = os.path.join(EXTRACTED_DIR, frame)

        frame_details = {}
        frame_details['frame_name'] = frame

        # initialize the count variables for a frame
        happy_count = 0
        sad_count = 0
        angry_count = 0
        neutral_count = 0
        surprise_count = 0

        # to count the extracted detections for a frame
        detection_count = 0

        for detections in os.listdir(FRAME_FOLDER):

            # only take the images with the student name
            if "frame" not in detections:
                # get the label for this image
                IMAGE_PATH = os.path.join(FRAME_FOLDER, detections)
                image = cv2.imread(IMAGE_PATH)

                label = emotion_recognition(classifier, face_classifier, image)

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

    # sort the recognitions based on the frame number
    sorted_activity_frame_recognitions = cs.custom_object_sorter(frame_emotion_recognitions)

    # return the detected frame percentages
    return sorted_activity_frame_recognitions


# this method will retrieve student activity summary for given time period
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

    individual_lec_emotions = []

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

    percentages = {}
    percentages["happy_perct"] = happy_average_perct
    percentages["sad_perct"] = sad_average_perct
    percentages["angry_perct"] = angry_average_perct
    percentages["disgust_perct"] = disgust_average_perct
    percentages["surprise_perct"] = surprise_average_perct
    percentages["neutral_perct"] = neutral_average_perct

    return percentages, individual_lec_emotions, emotion_labels


# this method will retrieve activity frame groupings for a lecture
def emotion_frame_groupings(video_name, frame_landmarks, frame_group_dict):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))

    # load the models
    face_classifier = cv2.CascadeClassifier(
        os.path.join(BASE_DIR, 'FirstApp\classifiers\haarcascade_frontalface_default.xml'))
    classifier_path = os.path.join(BASE_DIR, 'FirstApp\classifiers\Emotion_little_vgg.h5')
    classifier = load_model(classifier_path)



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
    for frame in os.listdir(EXTRACTED_DIR):
        # getting the frame folder
        FRAME_FOLDER = os.path.join(EXTRACTED_DIR, frame)

        # initializing the variables
        happy_count = 0
        sad_count = 0
        angry_count = 0
        surprise_count = 0
        neutral_count = 0
        detection_count = 0

        # looping through the detections in each frame
        for detections in os.listdir(FRAME_FOLDER):

            # checking whether the image contains only one person
            if "frame" not in detections:
                # get the label for this image
                IMAGE_PATH = os.path.join(FRAME_FOLDER, detections)
                image = cv2.imread(IMAGE_PATH)

                # run the model and get the emotion label
                label = emotion_recognition(classifier, face_classifier, image)

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

        # print('frame group phone count: ', frame_group_phone_count)
        # print('frame group listen count: ', frame_group_listen_count)
        # print('frame group note count: ', frame_group_note_count)
        # print('frame group detection count: ', group_detection_count)

        frame_diff = int(frame_group_diff[key])

        # print('frame difference: ', frame_diff)

        frame_group_happy_perct = float(frame_group_happy_count / group_detection_count) * 100
        frame_group_sad_perct = float(frame_group_sad_count / group_detection_count) * 100
        frame_group_angry_perct = float(frame_group_angry_count / group_detection_count) * 100
        frame_group_surprise_perct = float(frame_group_surprise_count / group_detection_count) * 100
        frame_group_neutral_perct = float(frame_group_neutral_count / group_detection_count) * 100

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