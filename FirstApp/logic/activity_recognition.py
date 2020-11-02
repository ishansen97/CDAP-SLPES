import tensorflow as tf
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
import os
import shutil
from .custom_sorter import *
from ..MongoModels import *
from ..serializers import *
from . import id_generator as ig
from . import utilities as ut

import pandas as pd


def activity_recognition(video_path):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_path))
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_03.h5")
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_04.h5")
    ACTIVITY_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\activity")

    # files required for person detection
    config_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.prototxt.txt")
    model_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.caffemodel")

    # load our serialized persosn detection model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(config_file, model_file)

    # dictionary to hold the percentage values
    percentages = {}

    np.set_printoptions(suppress=True)

    # class_labels = ['Phone checking', 'Talking with friends', 'note taking']
    # class labels
    class_labels = ['Phone checking', 'Listening', 'Note taking']

    model = tensorflow.keras.models.load_model(CLASSIFIER_DIR)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    # iteration
    video = cv2.VideoCapture(VIDEO_DIR)
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_count = 0
    total_detections = 0
    phone_checking_count = 0
    note_taking_count = 0
    listening_count = 0

    # for testing purposes
    print('starting the activity recognition process')

    while (frame_count < no_of_frames):
        ret, image = video.read()

        image = cv2.resize(image, size)
        detections = person_detection(image, net)

        # this is for testing purposes
        print('frame count: ', frame_count)


        # if there are any person detections
        if (len(detections) > 0):

            total_detections += len(detections)

            detection_count = 0

            # looping through the person detections of the frame
            for detection in detections:

                detection = cv2.resize(detection, size)

                image_array = np.asarray(detection)
                normalized_image_array = (detection.astype(np.float32) / 127.0) - 1

                # Load the image into the array
                data[0] = normalized_image_array

                # run the inference
                prediction = model.predict(data)
                # print('the prediction: ', prediction)
                label = class_labels[prediction.argmax()]

                # counting the detections under each label
                if (label == class_labels[0]):
                    phone_checking_count += 1
                elif (label == class_labels[1]):
                    listening_count += 1
                elif (label == class_labels[2]):
                    note_taking_count += 1


                detection_count += 1

        frame_count += 1


    # calculating the percentages for each label
    phone_perct = float(phone_checking_count / total_detections) * 100 if total_detections > 0 else 0
    # talking_perct = float(talking_count / total_detections) * 100 if total_detections > 0 else 0
    note_perct = float(note_taking_count / total_detections) * 100 if total_detections > 0 else 0
    listening_perct = float(listening_count / total_detections) * 100 if total_detections > 0 else 0

    # assigning the percentages to the dictionary
    percentages["phone_perct"] = phone_perct
    # percentages["talking_perct"] = talking_perct
    percentages["writing_perct"] = note_perct
    percentages["listening_perct"] = listening_perct

    # for testing purposes
    print('activity recognition process is over')

    return percentages


def person_detection(image, net):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    threshold = 0.2
    detected_person = []

    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    person_count = 0

    # load the input image and construct an input blob for the image
    # by resizing to a fixed 300x300 pixels and then normalizing it
    # (note: normalization is done via the authors of the MobileNet SSD
    # implementation)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > threshold:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)

            # print("[INFO] {}".format(label))

            if (format(label).__contains__("person")):
                startX = 0 if startX < 0 else startX
                startY = 0 if startY < 0 else startY

                person = image[startY:startY + endY, startX:startX + endX]
                detected_person.append(person)

                person_count += 1

    return detected_person


# retrieving the extracted frames and detections for a given video
def getExtractedFrames(folder_name):
    image_list = []

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(folder_name))

    # listing all the images in the directory
    for frame_folders in os.listdir(EXTRACTED_DIR):
        FRAME_FOLDER = os.path.join(EXTRACTED_DIR, frame_folders)
        frame_details = {}
        frame_details['frame'] = frame_folders
        detection_details = []

        for detections in os.listdir(FRAME_FOLDER):
            detection_details.append(detections)

        frame_details['detections'] = detection_details
        image_list.append(frame_details)

    # checking for the number of frames
    if (len(image_list) > 0):
        image_list = custom_object_sorter(image_list)
        return image_list

    else:
        return "No extracted frames were found"


# get detections for a given frame name
def get_detections(video_name, frame_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))
    FRAME_DIR = os.path.join(EXTRACTED_DIR, frame_name)
    detections = []

    for detection in os.listdir(FRAME_DIR):
        if 'frame' not in detection:
            detections.append(detection)

    return detections


# get detections for a given class name
def get_detections_for_label(video_name, label_index):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")

    np.set_printoptions(suppress=True)

    model = tensorflow.keras.models.load_model(CLASSIFIER_DIR)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    class_labels = ['Phone checking', 'Talking with friends', 'note taking']

    label_index = int(label_index)

    given_label = class_labels[label_index]

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

                image = cv2.resize(image, size)

                image_array = np.asarray(image)
                normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

                # Load the image into the array
                data[0] = normalized_image_array

                # run the inference
                prediction = model.predict(data)

                label = class_labels[prediction.argmax()]

                # checking for equality in selected label and given label
                if (label == given_label):
                    detected_images.append(detection)
                    detections.append(detection)

        frame_details['detections'] = detected_images
        frames.append(frame_details)

    sorted_frames = custom_object_sorter(frames)
    set_detections = set(detections)
    list_set_detections = list(set_detections)

    sorted_list_set_detections = custom_sort(list_set_detections)

    return sorted_frames, sorted_list_set_detections


# to get the student evaluations
def get_student_activity_evaluation(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_03.h5")
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_04.h5")

    np.set_printoptions(suppress=True)

    model = tensorflow.keras.models.load_model(CLASSIFIER_DIR)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    class_labels = ['Phone checking', 'Talking with friends', 'note taking']

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

                image = cv2.resize(image, size)

                image_array = np.asarray(image)
                normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

                # Load the image into the array
                data[0] = normalized_image_array

                # run the inference
                prediction = model.predict(data)

                label = class_labels[prediction.argmax()]

                detected_images.append(detection)
                detections.append(detection)

        frame_details['detections'] = detected_images
        frames.append(frame_details)

    sorted_frames = custom_object_sorter(frames)
    set_detections = set(detections)
    list_set_detections = list(set_detections)

    sorted_list_set_detections = custom_sort(list_set_detections)

    return sorted_frames, sorted_list_set_detections


# recognize the activity for each frame
def get_frame_activity_recognition(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_03.h5")
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_04.h5")
    ACTIVITY_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\activity")

    # files required for person detection
    config_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.prototxt.txt")
    model_file = os.path.join(BASE_DIR, "FirstApp\\classifiers\\MobileNetSSD_deploy.caffemodel")

    # load our serialized persosn detection model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(config_file, model_file)


    np.set_printoptions(suppress=True)

    # class_labels = ['Phone checking', 'Talking with friends', 'note taking']
    # class labels
    class_labels = ['Phone checking', 'Listening', 'Note taking']

    model = tensorflow.keras.models.load_model(CLASSIFIER_DIR)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    # iteration
    video = cv2.VideoCapture(VIDEO_DIR)
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_count = 0



    # frame activity recognitions
    frame_activity_recognitions = []


    # for testing purposes
    print('starting the frame activity recognition process')

    # looping through the frames
    while (frame_count < no_of_frames):

        # define the count variables for each frame
        phone_checking_count = 0
        listening_count = 0
        note_taking_count = 0

        ret, image = video.read()

        # derive the frame folder path
        # FRAME_FOLDER = os.path.join(EXTRACTED_DIR, frame)

        frame_name = "frame-{}".format(frame_count)

        frame_details = {}
        frame_details['frame_name'] = frame_name

        # to count the extracted detections for a frame
        detection_count = 0
        detected_percentages = []

        detections = person_detection(image, net)


        # if there are detections
        if (len(detections) > 0):

            # loop through each detection in the frame
            for detection in detections:

                detection = cv2.resize(detection, size)

                image_array = np.asarray(detection)
                normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

                # Load the image into the array
                data[0] = normalized_image_array

                # run the inference
                prediction = model.predict(data)

                label = class_labels[prediction.argmax()]

                # increment the relevant count, based on the label
                if (label == class_labels[0]):
                    phone_checking_count += 1
                elif (label == class_labels[1]):
                    listening_count += 1
                elif (label == class_labels[2]):
                    note_taking_count += 1

                # increment the detection count
                detection_count += 1


            # calculating the percentages for the frame
            phone_checking_perct = float(phone_checking_count / detection_count) * 100 if detection_count > 0 else 0
            listening_perct = float(listening_count / detection_count) * 100 if detection_count > 0 else 0
            note_taking_perct = float(note_taking_count / detection_count) * 100 if detection_count > 0 else 0

            # adding the percentage values to the frame details
            frame_details['phone_perct'] = phone_checking_perct
            frame_details['listening_perct'] = listening_perct
            frame_details['note_perct'] = note_taking_perct

            # push to all the frame details
            frame_activity_recognitions.append(frame_details)

        else:
            break


        print('current frame: ', frame_count)
        # increment frame count
        frame_count += 1


    # sort the recognitions based on the frame number
    sorted_activity_frame_recognitions = custom_object_sorter(frame_activity_recognitions)

    # for testing purposes
    print('ending the frame activity recognition process')

    # return the detected frame percentages
    return sorted_activity_frame_recognitions



# this method will retrieve individual student evaluation
def get_individual_student_evaluation(video_name, student_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_03.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_04.h5")
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_05.h5")

    np.set_printoptions(suppress=True)

    # load the model
    model = tensorflow.keras.models.load_model(CLASSIFIER_DIR)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    # initializing the count variables
    frame_count = 0
    phone_count = 0
    note_count = 0
    listen_count = 0

    # class labels
    class_labels = ['Phone checking', 'Listening', 'Note taking']

    for frame in os.listdir(EXTRACTED_DIR):
        # getting the frame folder
        FRAME_FOLDER = os.path.join(EXTRACTED_DIR, frame)

        for detections in os.listdir(FRAME_FOLDER):

            # only take the images with the student name
            if detections == student_name:
                # get the label for this image
                IMAGE_PATH = os.path.join(FRAME_FOLDER, detections)
                image = cv2.imread(IMAGE_PATH)

                image = cv2.resize(image, size)

                image_array = np.asarray(image)
                normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

                # Load the image into the array
                data[0] = normalized_image_array

                # run the inference
                prediction = model.predict(data)

                label = class_labels[prediction.argmax()]

                # checking for the label
                if label == class_labels[0]:
                    phone_count += 1
                elif label == class_labels[1]:
                    listen_count += 1
                elif label == class_labels[2]:
                    note_count += 1

        # increment the frame count
        frame_count += 1

    # calculating the percentages
    phone_perct = float(phone_count / frame_count) * 100
    writing_perct = float(note_count / frame_count) * 100
    listening_perct = float(listen_count / frame_count) * 100

    # this dictionary will be returned
    percentages = {}
    percentages['phone_perct'] = phone_perct
    percentages['writing_perct'] = writing_perct
    percentages['listening_perct'] = listening_perct

    return percentages


# this method will retrieve student activity summary for given time period
def get_student_activity_summary_for_period(activities):
    # declare variables to add percentage values
    phone_checking_perct_combined = 0.0
    listening_perct_combined = 0.0
    note_taking_perct_combined = 0.0

    # get the number of activties to calculate average
    no_of_activities = len(activities)

    individual_lec_activities = []

    activity_labels = ["phone_perct", "listening_perct", "writing_perct"]

    # iterate through the activities
    for activity in activities:
        individual_activity = {}
        individual_activity["phone_perct"] = float(activity['phone_perct'])
        individual_activity["listening_perct"] = float(activity['listening_perct'])
        individual_activity["writing_perct"] = float(activity['writing_perct'])

        phone_checking_perct_combined += float(activity['phone_perct'])
        listening_perct_combined += float(activity['listening_perct'])
        note_taking_perct_combined += float(activity['writing_perct'])

        # append to the list
        individual_lec_activities.append(individual_activity)

    # calculate the average percentages
    phone_checking_average_perct = round((phone_checking_perct_combined / no_of_activities), 1)
    listening_average_perct = round((listening_perct_combined / no_of_activities), 1)
    note_taking_average_perct = round((note_taking_perct_combined / no_of_activities), 1)

    percentages = {}
    percentages["phone_perct"] = phone_checking_average_perct
    percentages["listening_perct"] = listening_average_perct
    percentages["writing_perct"] = note_taking_average_perct

    return percentages, individual_lec_activities, activity_labels


# this method will retrieve activity frame groupings for a lecture
def activity_frame_groupings(video_name, frame_landmarks, frame_group_dict):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_03.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_04.h5")
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_05.h5")

    np.set_printoptions(suppress=True)

    # load the model
    model = tensorflow.keras.models.load_model(CLASSIFIER_DIR)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    # initializing the count variables
    frame_count = 0

    # class labels
    class_labels = ['Phone checking', 'Listening', 'Note taking']

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
        phone_count = 0
        note_count = 0
        listen_count = 0
        detection_count = 0

        # looping through the detections in each frame
        for detections in os.listdir(FRAME_FOLDER):

            # checking whether the image contains only one person
            if "frame" not in detections:
                # get the label for this image
                IMAGE_PATH = os.path.join(FRAME_FOLDER, detections)
                image = cv2.imread(IMAGE_PATH)

                image = cv2.resize(image, size)

                image_array = np.asarray(image)
                normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

                # Load the image into the array
                data[0] = normalized_image_array

                # run the inference
                prediction = model.predict(data)

                # get the predicted label
                label = class_labels[prediction.argmax()]

                # increment the count based on the label
                if label == class_labels[0]:
                    phone_count += 1
                elif label == class_labels[1]:
                    listen_count += 1
                elif label == class_labels[2]:
                    note_count += 1

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

                            frame_group_dict[frame_name]['phone_count'] += phone_count
                            frame_group_dict[frame_name]['listen_count'] += listen_count
                            frame_group_dict[frame_name]['note_count'] += note_count
                            frame_group_dict[frame_name]['detection_count'] += detection_count

        # increment the frame count
        frame_count += 1

    # calculate the percentage values
    for key in frame_group_dict.keys():
        frame_group_details = frame_group_dict[key]
        frame_group_phone_count = frame_group_details['phone_count']
        frame_group_listen_count = frame_group_details['listen_count']
        frame_group_note_count = frame_group_details['note_count']
        group_detection_count = frame_group_details['detection_count']

        # print('frame group phone count: ', frame_group_phone_count)
        # print('frame group listen count: ', frame_group_listen_count)
        # print('frame group note count: ', frame_group_note_count)
        # print('frame group detection count: ', group_detection_count)

        frame_diff = int(frame_group_diff[key])

        # print('frame difference: ', frame_diff)

        frame_group_phone_perct = float(frame_group_phone_count / group_detection_count) * 100
        frame_group_listen_perct = float(frame_group_listen_count / group_detection_count) * 100
        frame_group_note_perct = float(frame_group_note_count / group_detection_count) * 100

        # assign the values to the same dictionary
        frame_group_dict[key]['phone_perct'] = round(frame_group_phone_perct, 1)
        frame_group_dict[key]['listen_perct'] = round(frame_group_listen_perct, 1)
        frame_group_dict[key]['note_perct'] = round(frame_group_note_perct, 1)

        # removing irrelevant items from the dictionary
        frame_group_dict[key].pop('phone_count')
        frame_group_dict[key].pop('listen_count')
        frame_group_dict[key].pop('note_count')
        frame_group_dict[key].pop('detection_count')

    # print('frame group dict: ', frame_group_dict)
    activity_labels = ['phone_perct', 'listen_perct', 'note_perct']

    # return the dictionary
    return frame_group_dict, activity_labels


# this section will handle saving activity entities to the database
def save_frame_recognition(video_name):

    # for testing purposes
    print('starting the saving activity frame recognition process')

    # retrieve the lecture activity id
    lec_activity = LectureActivity.objects.filter(lecture_video_id__video_name=video_name)
    lec_activity_ser = LectureActivitySerializer(lec_activity, many=True)
    lec_activity_data = lec_activity_ser.data[0]
    lec_activity_id = lec_activity_data['id']

    # create a new lecture activity frame detections id
    last_lec_activity_frame_recognitions = LectureActivityFrameRecognitions.objects.order_by(
        'lecture_activity_frame_recognition_id').last()
    new_lecture_activity_frame_recognitions_id = "LAFR00001" if (last_lec_activity_frame_recognitions is None) else \
        ig.generate_new_id(last_lec_activity_frame_recognitions.lecture_activity_frame_recognition_id)

    # calculate the frame detections
    frame_detections = get_frame_activity_recognition(video_name)

    frame_recognition_details = []

    # save the new lecture activity frame recognitions
    for detection in frame_detections:
        lec_activity_frame_recognition_details = LectureActivityFrameRecognitionDetails()
        lec_activity_frame_recognition_details.frame_name = detection['frame_name']
        lec_activity_frame_recognition_details.phone_perct = detection['phone_perct']
        lec_activity_frame_recognition_details.listen_perct = detection['listening_perct']
        lec_activity_frame_recognition_details.note_perct = detection['note_perct']

        frame_recognition_details.append(lec_activity_frame_recognition_details)

    lec_activity_frame_recognitions = LectureActivityFrameRecognitions()
    lec_activity_frame_recognitions.lecture_activity_frame_recognition_id = new_lecture_activity_frame_recognitions_id
    lec_activity_frame_recognitions.lecture_activity_id_id = lec_activity_id
    lec_activity_frame_recognitions.frame_recognition_details = frame_recognition_details

    lec_activity_frame_recognitions.save()

    # for testing purposes
    print('ending the saving activity frame recognition process')

    # now return the frame detections
    return frame_detections


# this method will save the activity frame groupings to the database
def save_frame_groupings(video_name, frame_landmarks, frame_group_dict):

    # for testing purposes
    print('starting the saving activity frame groupings process')

    frame_group_percentages, activity_labels = activity_frame_groupings(video_name, frame_landmarks,
                                                                           frame_group_dict)

    # save the frame group details into db
    last_lec_activity_frame_grouping = LectureActivityFrameGroupings.objects.order_by(
        'lecture_activity_frame_groupings_id').last()
    new_lecture_activity_frame_grouping_id = "LAFG00001" if (last_lec_activity_frame_grouping is None) else \
        ig.generate_new_id(last_lec_activity_frame_grouping.lecture_activity_frame_groupings_id)

    # retrieve the lecture activity id
    lec_activity = LectureActivity.objects.filter(lecture_video_id__video_name=video_name)
    lec_activity_ser = LectureActivitySerializer(lec_activity, many=True)
    lec_activity_id = lec_activity_ser.data[0]['id']

    # create the frame group details
    frame_group_details = []

    for key in frame_group_percentages.keys():
        # create an object of type 'LectureActivityFrameGroupDetails'
        lec_activity_frame_group_details = LectureActivityFrameGroupDetails()
        lec_activity_frame_group_details.frame_group = key
        lec_activity_frame_group_details.frame_group_percentages = frame_group_percentages[key]

        frame_group_details.append(lec_activity_frame_group_details)

    new_lec_activity_frame_groupings = LectureActivityFrameGroupings()
    new_lec_activity_frame_groupings.lecture_activity_frame_groupings_id = new_lecture_activity_frame_grouping_id
    new_lec_activity_frame_groupings.lecture_activity_id_id = lec_activity_id
    new_lec_activity_frame_groupings.frame_group_details = frame_group_details

    # for testing purposes
    print('ending the saving activity frame groupings process')

    # save
    new_lec_activity_frame_groupings.save()


# this method will get activity correlations
def get_activity_correlations(individual_lec_activities, lec_recorded_activity_data):

    # this variable will be used to store the correlations
    correlations = []

    limit = 10

    data_index = ['lecture-{}'.format(i+1)  for i in range(len(individual_lec_activities))]

    # student activity labels
    student_activity_labels = ['phone checking', 'listening', 'note taking']
    lecturer_activity_labels = ['seated', 'standing', 'walking']

    # lecturer recorded data list (lecturer)
    sitting_perct_list = []
    standing_perct_list = []
    walking_perct_list = []

    # lecture activity data list (student)
    phone_perct_list = []
    listen_perct_list = []
    note_perct_list = []

    # loop through the lecturer recorded data (lecturer)
    for data in lec_recorded_activity_data:
        sitting_perct_list.append(int(data['seated_count']))
        standing_perct_list.append(int(data['standing_count']))
        walking_perct_list.append(int(data['walking_count']))

   # loop through the lecturer recorded data (student)
    for data in individual_lec_activities:
        phone_perct_list.append(int(data['phone_perct']))
        listen_perct_list.append(int(data['listening_perct']))
        note_perct_list.append(int(data['writing_perct']))


    corr_data = {'phone checking': phone_perct_list, 'listening': listen_perct_list, 'note taking': note_perct_list,
                         'seated': sitting_perct_list, 'standing': standing_perct_list, 'walking': walking_perct_list}

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

    print('====correlated variables=====')
    print(pd_series)

    for i in range(limit):
        # this dictionary will get the pandas.Series object's  indices and values separately
        corr_dict = {}

        index = pd_series.index[i]

        # check whether the first index is a student activity
        isStudentAct = index[0] in student_activity_labels
        # check whether the second index is a lecturer activity
        isLecturerAct = index[1] in lecturer_activity_labels

        # if both are student and lecturer activities, add to the doctionary
        if isStudentAct & isLecturerAct:
            corr_dict['index'] = index
            corr_dict['value'] = pd_series.values[i]

            # append the dictionary to the 'correlations' list
            correlations.append(corr_dict)


    # return the list
    return correlations

