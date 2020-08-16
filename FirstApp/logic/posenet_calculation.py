import tensorflow as tf
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
import os
import math
import shutil
from . import custom_sorter as cs


def get_pose_estimations(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


# calculate pose estimations for a student
def calculate_pose_estimation_for_student(video_name, student, poses):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\activity\\{}".format(video_name))
    POSE_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\poses")
    POSE_VIDEO_DIR = os.path.join(POSE_DIR, video_name)
    pose_count = 0

    # checking whether the pose directory
    if os.path.isdir(POSE_VIDEO_DIR) == False:
        # create the pose directory
        os.mkdir(POSE_VIDEO_DIR)


    # loop through each frame of the directory
    for frame in os.listdir(VIDEO_DIR):

        FRAME_FOLDER = os.path.join(VIDEO_DIR, frame)

        for detection in os.listdir(FRAME_FOLDER):

            DETECTION_PATH = os.path.join(FRAME_FOLDER, detection)
            # detection image
            detection_img = cv2.imread(DETECTION_PATH)

            # checking for the given student
            if detection == student:

                # select the correct pose detection
                pose = poses[pose_count]

                # extract the coordinates
                x1 = int(pose['keypoints'][5]['position']['x'])
                y1 = int(pose['keypoints'][5]['position']['y'])
                x2 = int(pose['keypoints'][6]['position']['x'])
                y2 = int(pose['keypoints'][6]['position']['y'])

                # extract the head positions
                x_diff = x1 - x2
                y_diff = y1 - y2
                x_pow = math.pow(x_diff, 2)
                y_pow = math.pow(y_diff, 2)
                summation = x_pow + y_pow

                distance = int(math.sqrt(summation))

                # defining the hyperparameter
                param = 0.6

                fraction = int(math.floor(distance * param)) if int(math.floor(distance * param)) > 0 else 1

                middle_x = x2 + fraction

                # middle_y = y2 - 20
                middle_y = y2

                head_x = middle_x

                head_y = 0 if (middle_y - fraction) < 0 else (middle_y - fraction)

                left_upper_x = 0 if (middle_x - fraction) < 0 else (middle_x - fraction)

                print('head_y: ', head_y)
                print('fraction: ', fraction)
                print('distance: ', distance)
                print('left_upper_x: ', left_upper_x)

                # extract the new image
                new_img = detection_img[head_y:head_y+fraction, left_upper_x:left_upper_x+distance]

                # new directory name
                # new_img_dir = os.path.join(POSE_VIDEO_DIR, frame)
                new_img_dir = os.path.join(POSE_VIDEO_DIR, detection)

                # check if the directory exists
                if os.path.isdir(new_img_dir) == False:
                    # create the new directory
                    os.mkdir(new_img_dir)

                # create new image name
                frame_name = frame + ".png"

                new_img_path = os.path.join(new_img_dir, frame_name)

                # saving the new image
                cv2.imwrite(new_img_path, new_img)

                # increment the count
                pose_count += 1

                print('saving the image')


