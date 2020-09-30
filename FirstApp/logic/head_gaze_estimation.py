# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 03:00:36 2020

@author: hp
"""
from decimal import Decimal
from . custom_sorter import *

import cv2
import numpy as np
import math
from . face_detector import get_face_detector, find_faces
from . face_landmarks import get_landmark_model, detect_marks
import os
import shutil
import math


def get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val):
    """Return the 3D points present as 2D for making annotation box"""
    point_3d = []
    dist_coeffs = np.zeros((4, 1))
    rear_size = val[0]
    rear_depth = val[1]
    point_3d.append((-rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, -rear_size, rear_depth))

    front_size = val[2]
    front_depth = val[3]
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d.append((-front_size, front_size, front_depth))
    point_3d.append((front_size, front_size, front_depth))
    point_3d.append((front_size, -front_size, front_depth))
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d = np.array(point_3d, dtype=np.float).reshape(-1, 3)

    # Map to 2d img points
    (point_2d, _) = cv2.projectPoints(point_3d,
                                      rotation_vector,
                                      translation_vector,
                                      camera_matrix,
                                      dist_coeffs)
    point_2d = np.int32(point_2d.reshape(-1, 2))
    return point_2d


def draw_annotation_box(img, rotation_vector, translation_vector, camera_matrix,
                        rear_size=300, rear_depth=0, front_size=500, front_depth=400,
                        color=(255, 255, 0), line_width=2):
    """
    Draw a 3D anotation box on the face for head pose estimation

    Parameters
    ----------
    img : np.unit8
        Original Image.
    rotation_vector : Array of float64
        Rotation Vector obtained from cv2.solvePnP
    translation_vector : Array of float64
        Translation Vector obtained from cv2.solvePnP
    camera_matrix : Array of float64
        The camera matrix
    rear_size : int, optional
        Size of rear box. The default is 300.
    rear_depth : int, optional
        The default is 0.
    front_size : int, optional
        Size of front box. The default is 500.
    front_depth : int, optional
        Front depth. The default is 400.
    color : tuple, optional
        The color with which to draw annotation box. The default is (255, 255, 0).
    line_width : int, optional
        line width of lines drawn. The default is 2.

    Returns
    -------
    None.

    """

    rear_size = 1
    rear_depth = 0
    front_size = img.shape[1]
    front_depth = front_size * 2
    val = [rear_size, rear_depth, front_size, front_depth]
    point_2d = get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val)
    # # Draw all the lines
    cv2.polylines(img, [point_2d], True, color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[1]), tuple(
        point_2d[6]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[2]), tuple(
        point_2d[7]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[3]), tuple(
        point_2d[8]), color, line_width, cv2.LINE_AA)


def head_pose_points(img, rotation_vector, translation_vector, camera_matrix):
    """
    Get the points to estimate head pose sideways

    Parameters
    ----------
    img : np.unit8
        Original Image.
    rotation_vector : Array of float64
        Rotation Vector obtained from cv2.solvePnP
    translation_vector : Array of float64
        Translation Vector obtained from cv2.solvePnP
    camera_matrix : Array of float64
        The camera matrix

    Returns
    -------
    (x, y) : tuple
        Coordinates of line to estimate head pose

    """
    rear_size = 1
    rear_depth = 0
    front_size = img.shape[1]
    front_depth = front_size * 2
    val = [rear_size, rear_depth, front_size, front_depth]
    point_2d = get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val)
    y = (point_2d[5] + point_2d[8]) // 2
    x = point_2d[2]

    return (x, y)


# this method will perform gaze estimation for a lecture
def process_gaze_estimation(video_path):

    # get the base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_path))
    GAZE_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\gaze")

    # create a folder with the same name as the video
    VIDEO_DIR = os.path.join(GAZE_DIR, video_path)

    # define a dictionary to return the percentage values
    percentages = {}

    # checking whether the video directory exist
    if os.path.isdir(VIDEO_DIR):
        shutil.rmtree(VIDEO_DIR)

    # create the new directory
    os.mkdir(VIDEO_DIR)

    # load the face detection model
    face_model = get_face_detector()
    # load the facial landamrk model
    landmark_model = get_landmark_model()
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, img = cap.read()
    size = img.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner
    ])

    # setting up the count variables
    head_front_count = 0
    head_up_right_count = 0
    head_up_left_count = 0
    head_down_right_count = 0
    head_down_left_count = 0

    # define a variable to count the frames
    frame_count = 0
    face_count = 0

    # set a threshold angle
    # THRESHOLD = 15
    THRESHOLD = 22
    # THRESHOLD = 30
    # THRESHOLD = 45
    # THRESHOLD = 48

    # Camera internals
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    # iterate the video frames
    while True:
        ret, img = cap.read()
        if ret == True:
            faces = find_faces(img, face_model)

            # print('no of faces found: ', len(faces))
            student_count = 0

            # iterate through each detected face
            for face in faces:

                # declaring boolean variables
                isLookingUp = False
                isLookingDown = False
                isLookingRight = False
                isLookingLeft = False
                isLookingFront = False

                # deriving the student name to display in the image
                student_name = 'student-{}'.format(student_count)

                # retrieving the facial landmarks and face bounding box coordinates
                marks, facebox = detect_marks(img, landmark_model, face)
                # mark_detector.draw_marks(img, marks, color=(0, 255, 0))
                image_points = np.array([
                    marks[30],  # Nose tip
                    marks[8],  # Chin
                    marks[36],  # Left eye left corner
                    marks[45],  # Right eye right corne
                    marks[48],  # Left Mouth corner
                    marks[54]  # Right mouth corner
                ], dtype="double")
                dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
                (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                              dist_coeffs, flags=cv2.SOLVEPNP_UPNP)

                # Project a 3D point (0, 0, 1000.0) onto the image plane.
                # We use this to draw a line sticking out of the nose

                (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                                 translation_vector, camera_matrix, dist_coeffs)


                p1 = (int(image_points[0][0]), int(image_points[0][1]))
                p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
                x1, x2 = head_pose_points(img, rotation_vector, translation_vector, camera_matrix)

                # measuring the angles
                try:
                    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
                    ang1 = int(math.degrees(math.atan(m)))
                except:
                    ang1 = 90

                try:
                    m = (x2[1] - x1[1]) / (x2[0] - x1[0])
                    ang2 = int(math.degrees(math.atan(-1 / m)))
                except:
                    ang2 = 90

                # print('angle 1: {}, angle 2: {}'.format(ang1, ang2))
                # checking for angle 1
                if ang1 >= THRESHOLD:
                    # cv2.putText(img, 'looking down', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingDown = True
                elif ang1 <= -THRESHOLD:
                    # cv2.putText(img, 'looking up', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingUp = True
                else:
                    # cv2.putText(img, 'looking front', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingFront = True

                # checking for angle 2
                if ang2 >= THRESHOLD:
                    # cv2.putText(img, 'looking right', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingRight = True
                elif ang2 <= -THRESHOLD:
                    # cv2.putText(img, 'looking left', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingLeft = True

                # checking for vertical and horizontal directions
                if isLookingDown & isLookingRight:
                    cv2.putText(img, 'looking down and right', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_down_right_count += 1
                elif isLookingDown & isLookingLeft:
                    cv2.putText(img, 'looking down and left', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_down_left_count += 1
                elif isLookingUp & isLookingRight:
                    cv2.putText(img, 'looking up and right', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_up_right_count += 1
                elif isLookingUp & isLookingLeft:
                    cv2.putText(img, 'looking up and left', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_up_left_count += 1
                elif isLookingFront:
                    cv2.putText(img, 'Head front', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_front_count += 1

                # indicate the student name
                cv2.putText(img, student_name, (facebox[2], facebox[3]), font, 2, (255, 255, 128), 3)

                # increment the face count
                face_count += 1

            # naming the new image
            image_name = "frame-{}.png".format(frame_count)

            # new image path
            image_path = os.path.join(VIDEO_DIR, image_name)

            # save the new image
            cv2.imwrite(image_path, img)

            # increment the frame count
            frame_count += 1

        else:
            break


    # after extracting the frames, save the changes to static content
    p = os.popen("python manage.py collectstatic", "w")
    p.write("yes")

    # calculate percentages
    head_up_right_perct = (Decimal(head_up_right_count) / Decimal(face_count)) * 100
    head_up_left_perct = (Decimal(head_up_left_count) / Decimal(face_count)) * 100
    head_down_right_perct = (Decimal(head_down_right_count) / Decimal(face_count)) * 100
    head_down_left_perct = (Decimal(head_down_left_count) / Decimal(face_count)) * 100
    head_front_perct = (Decimal(head_front_count) / Decimal(face_count)) * 100



    # collect the percentages to a dictionary
    percentages['head_up_right_perct'] = head_up_right_perct
    percentages['head_up_left_perct'] = head_up_left_perct
    percentages['head_down_right_perct'] = head_down_right_perct
    percentages['head_down_left_perct'] = head_down_left_perct
    percentages['head_front_perct'] = head_front_perct


    cv2.destroyAllWindows()
    cap.release()

    # return the dictionary
    return percentages

# this method will retrieve extracted frames
def getExtractedFrames(lecture_video_name):
    image_list = []

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\gaze\\{}".format(lecture_video_name))

    # listing all the images in the directory
    for image_path in os.listdir(EXTRACTED_DIR):
        image_list.append(image_path)

    # checking for the number of frames
    if (len(image_list) > 0):
        image_list = custom_sort(image_list)
        return image_list

    else:
        return "No extracted frames were found"


# this method will retrieve lecture gaze estimation for each frame
def get_lecture_gaze_esrimation_for_frames(video_name):

    # get the base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))

    # play the video
    video = cv2.VideoCapture(VIDEO_PATH)

    frame_rate = video.get(cv2.CAP_PROP_FPS)


    frame_detections = []


    face_model = get_face_detector()
    landmark_model = get_landmark_model()
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, img = cap.read()
    size = img.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner
    ])



    # define a variable to count the frames
    frame_count = 0

    # set a threshold angle
    # THRESHOLD = 15
    THRESHOLD = 22
    # THRESHOLD = 30
    # THRESHOLD = 45
    # THRESHOLD = 48

    # Camera internals
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    # iterate the video frames
    while True:
        ret, img = cap.read()
        if ret == True:

            # setting up the count variables
            head_front_count = 0
            head_up_right_count = 0
            head_up_left_count = 0
            head_down_right_count = 0
            head_down_left_count = 0
            face_count = 0

            # find the number of faces
            faces = find_faces(img, face_model)

            student_count = 0

            # iterate through each detected face
            for face in faces:

                # declaring boolean variables
                isLookingUp = False
                isLookingDown = False
                isLookingRight = False
                isLookingLeft = False
                isLookingFront = False

                # deriving the student name to display in the image
                student_name = 'student-{}'.format(student_count)

                # retrieving the facial landmarks and face bounding box coordinates
                marks, facebox = detect_marks(img, landmark_model, face)
                # mark_detector.draw_marks(img, marks, color=(0, 255, 0))
                image_points = np.array([
                    marks[30],  # Nose tip
                    marks[8],  # Chin
                    marks[36],  # Left eye left corner
                    marks[45],  # Right eye right corne
                    marks[48],  # Left Mouth corner
                    marks[54]  # Right mouth corner
                ], dtype="double")
                dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
                (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                              dist_coeffs, flags=cv2.SOLVEPNP_UPNP)

                # Project a 3D point (0, 0, 1000.0) onto the image plane.
                # We use this to draw a line sticking out of the nose

                (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                                 translation_vector, camera_matrix, dist_coeffs)

                p1 = (int(image_points[0][0]), int(image_points[0][1]))
                p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
                x1, x2 = head_pose_points(img, rotation_vector, translation_vector, camera_matrix)

                # measuring the angles
                try:
                    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
                    ang1 = int(math.degrees(math.atan(m)))
                except:
                    ang1 = 90

                try:
                    m = (x2[1] - x1[1]) / (x2[0] - x1[0])
                    ang2 = int(math.degrees(math.atan(-1 / m)))
                except:
                    ang2 = 90

                # print('angle 1: {}, angle 2: {}'.format(ang1, ang2))
                # checking for angle 1
                if ang1 >= THRESHOLD:
                    # cv2.putText(img, 'looking down', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingDown = True
                elif ang1 <= -THRESHOLD:
                    # cv2.putText(img, 'looking up', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingUp = True
                else:
                    # cv2.putText(img, 'looking front', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingFront = True

                # checking for angle 2
                if ang2 >= THRESHOLD:
                    # cv2.putText(img, 'looking right', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingRight = True
                elif ang2 <= -THRESHOLD:
                    # cv2.putText(img, 'looking left', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    isLookingLeft = True

                # checking for vertical and horizontal directions
                if isLookingDown & isLookingRight:
                    head_down_right_count += 1
                elif isLookingDown & isLookingLeft:
                    head_down_left_count += 1
                elif isLookingUp & isLookingRight:
                    head_up_right_count += 1
                elif isLookingUp & isLookingLeft:
                    head_up_left_count += 1
                elif isLookingFront:
                    head_front_count += 1



                # increment the face count
                face_count += 1


            # the percentages will be calculated here
            head_up_right_perct = (Decimal(head_up_right_count) / Decimal(face_count)) * 100 if (face_count != 0) else 0
            head_up_left_perct = (Decimal(head_up_left_count) / Decimal(face_count)) * 100 if (face_count != 0) else 0
            head_down_right_perct = (Decimal(head_down_right_count) / Decimal(face_count)) * 100 if (face_count != 0) else 0
            head_down_left_perct = (Decimal(head_down_left_count) / Decimal(face_count)) * 100 if (face_count != 0) else 0
            head_front_perct = (Decimal(head_front_count) / Decimal(face_count)) * 100 if (face_count != 0) else 0

            # the dictionary
            percentages = {}


            # collect the percentages to a dictionary
            percentages['frame_name'] = "frame-{}".format(frame_count)
            percentages['head_up_right_perct'] = head_up_right_perct
            percentages['head_up_left_perct'] = head_up_left_perct
            percentages['head_down_right_perct'] = head_down_right_perct
            percentages['head_down_left_perct'] = head_down_left_perct
            percentages['head_front_perct'] = head_front_perct

            # append the calculated percentages to the frame_detections
            frame_detections.append(percentages)

            frame_count += 1

        else:
            break



    return frame_detections, frame_rate


def get_student_gaze_estimation_summary_for_period(gaze_estimation_data):
    # declare variables to add percentage values
    phone_checking_perct_combined = 0.0
    listening_perct_combined = 0.0
    note_taking_perct_combined = 0.0

    looking_up_right_perct_combined = 0.0
    looking_up_left_perct_combined = 0.0
    looking_down_right_perct_combined = 0.0
    looking_down_left_perct_combined = 0.0
    looking_front_perct_combined = 0.0

    # get the number of activties to calculate average
    no_of_gaze_estimations = len(gaze_estimation_data)

    individual_lec_gaze_estimations = []

    gaze_estimation_labels = ["looking_up_and_right_perct", "looking_up_and_left_perct", "looking_down_and_right_perct", "looking_down_and_left_perct", "looking_front_perct"]

    # iterate through the activities
    for gaze_estimation in gaze_estimation_data:
        individual_gaze_estimation = {}
        individual_gaze_estimation["looking_up_and_right_perct"] = float(gaze_estimation['looking_up_and_right_perct'])
        individual_gaze_estimation["looking_up_and_left_perct"] = float(gaze_estimation['looking_up_and_left_perct'])
        individual_gaze_estimation["looking_down_and_right_perct"] = float(gaze_estimation['looking_down_and_right_perct'])
        individual_gaze_estimation["looking_down_and_left_perct"] = float(gaze_estimation['looking_down_and_left_perct'])
        individual_gaze_estimation["looking_front_perct"] = float(gaze_estimation['looking_front_perct'])

        looking_up_right_perct_combined += float(gaze_estimation['looking_up_and_right_perct'])
        looking_up_left_perct_combined += float(gaze_estimation['looking_up_and_left_perct'])
        looking_down_right_perct_combined += float(gaze_estimation['looking_down_and_right_perct'])
        looking_down_left_perct_combined += float(gaze_estimation['looking_down_and_left_perct'])
        looking_front_perct_combined += float(gaze_estimation['looking_front_perct'])

        # append to the list
        individual_lec_gaze_estimations.append(individual_gaze_estimation)

    # calculate the average percentages
    looking_up_right_average_perct = round((looking_up_right_perct_combined / no_of_gaze_estimations), 1)
    looking_up_left_perct = round((looking_up_left_perct_combined / no_of_gaze_estimations), 1)
    looking_down_right_average_perct = round((looking_down_right_perct_combined / no_of_gaze_estimations), 1)
    looking_down_left_average_perct = round((looking_down_left_perct_combined / no_of_gaze_estimations), 1)
    looking_front_average_perct = round((looking_front_perct_combined / no_of_gaze_estimations), 1)

    percentages = {}
    percentages["looking_up_and_right_perct"] = looking_up_right_average_perct
    percentages["looking_up_and_left_perct"] = looking_up_left_perct_combined
    percentages["looking_down_and_right_perct"] = looking_down_right_perct_combined
    percentages["looking_down_and_left_perct"] = looking_down_left_perct_combined
    percentages["looking_front_perct"] = looking_front_average_perct

    return percentages, individual_lec_gaze_estimations, gaze_estimation_labels