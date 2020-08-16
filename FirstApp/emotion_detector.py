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

        print('number of faces: ', len(faces))

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
                    # path = os.path.join(BASE_DIR, 'static\\images\\Sad')
                    # cv2.imwrite(os.path.join(path, 'Sad-{0}.jpg'.format(count)), frame)

                elif (label == 'Surprise'):
                    count_surprise += 1
                    # path = os.path.join(BASE_DIR, 'static\\images\\Surprise')
                    # cv2.imwrite(os.path.join(path, 'Surprise-{0}.jpg'.format(count)), frame)

                label_position = (x, y)
                # cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                # cv2.imwrite("".format(label, count), frame)
            else:
                cv2.putText(frame, 'No Face Found', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        # cv2.imshow('Emotion Detector',frame)
        count_frames += 1
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

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
        happy_perct = float(happy_count / detection_count) * 100
        sad_perct = float(sad_count / detection_count) * 100
        angry_perct = float(angry_count / detection_count) * 100
        neutral_perct = float(neutral_count / detection_count) * 100
        surprise_perct = float(surprise_count / detection_count) * 100

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