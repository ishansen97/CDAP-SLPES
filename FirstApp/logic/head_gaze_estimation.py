"""

this file contain the relevant methods to implement the student gaze estimation logic

main methods include
    * the execution of gaze estimation model and saving the results into the database,
    * retrieving the gaze estimation details for lectures within a given time period
    * calculating the gaze estimation details for each frame, for a given lecture
    * calculating the gaze estimation details for frame groups, for a given lecture
    * calculating the gaze estimation correlations with the lecturer posture activities



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
import pandas as pd

from ..MongoModels import *
from ..serializers import *
from . import id_generator as ig
from . import utilities as ut


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


    # define a dictionary to return the percentage values
    percentages = {}


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

    # for testing purposes
    print('starting the gaze estimation process')

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
                    # cv2.putText(img, 'looking down and right', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_down_right_count += 1
                elif isLookingDown & isLookingLeft:
                    # cv2.putText(img, 'looking down and left', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_down_left_count += 1
                elif isLookingUp & isLookingRight:
                    # cv2.putText(img, 'looking up and right', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_up_right_count += 1
                elif isLookingUp & isLookingLeft:
                    # cv2.putText(img, 'looking up and left', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_up_left_count += 1
                elif isLookingFront:
                    # cv2.putText(img, 'Head front', (facebox[0], facebox[1]), font, 2, (255, 255, 128), 3)
                    head_front_count += 1

                # indicate the student name
                # cv2.putText(img, student_name, (facebox[2], facebox[3]), font, 2, (255, 255, 128), 3)

                # increment the face count
                face_count += 1

            # naming the new image
            # image_name = "frame-{}.png".format(frame_count)
            #
            # # new image path
            # image_path = os.path.join(VIDEO_DIR, image_name)

            # save the new image
            # cv2.imwrite(image_path, img)


            # for testing purposes
            print('gaze estimation count: ', frame_count)

            # increment the frame count
            frame_count += 1

        else:
            break


    # after extracting the frames, save the changes to static content
    # p = os.popen("python manage.py collectstatic", "w")
    # p.write("yes")

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

    # for testing purposes
    print('ending the gaze estimation process')

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
def get_lecture_gaze_estimation_for_frames(video_name):

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


    # for testing purposes
    print('starting the gaze estimation for frames process')

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
            percentages['upright_perct'] = head_up_right_perct
            percentages['upleft_perct'] = head_up_left_perct
            percentages['downright_perct'] = head_down_right_perct
            percentages['downleft_perct'] = head_down_left_perct
            percentages['front_perct'] = head_front_perct

            # append the calculated percentages to the frame_detections
            frame_detections.append(percentages)

            # for testing purposes
            print('gaze estimation frame recognition count: ', frame_count)

            frame_count += 1

        else:
            break



    # for testing purposes
    print('ending the gaze estimation for frames process')

    # return the details
    return frame_detections, frame_rate


# this method will get the student gaze estimation summary for period
def get_student_gaze_estimation_summary_for_period(gaze_estimation_data):

    # declare variables to add percentage values
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
    looking_up_left_average_perct = round((looking_up_left_perct_combined / no_of_gaze_estimations), 1)
    looking_down_right_average_perct = round((looking_down_right_perct_combined / no_of_gaze_estimations), 1)
    looking_down_left_average_perct = round((looking_down_left_perct_combined / no_of_gaze_estimations), 1)
    looking_front_average_perct = round((looking_front_perct_combined / no_of_gaze_estimations), 1)

    percentages = {}
    percentages["looking_up_and_right_perct"] = looking_up_right_average_perct
    percentages["looking_up_and_left_perct"] = looking_up_left_average_perct
    percentages["looking_down_and_right_perct"] = looking_down_right_average_perct
    percentages["looking_down_and_left_perct"] = looking_down_left_average_perct
    percentages["looking_front_perct"] = looking_front_average_perct

    return percentages, individual_lec_gaze_estimations, gaze_estimation_labels


# this method will get the lecture gaze estimation frame groupings
def gaze_estimation_frame_groupings(video_name, frame_landmarks, frame_group_dict):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\gaze\\{}".format(video_name))
    VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\videos\\{}".format(video_name))

    print('video path: ', VIDEO_PATH)

    # load the face detection model
    face_model = get_face_detector()
    # load the facial landamrk model
    landmark_model = get_landmark_model()
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, img = cap.read()
    size = img.shape

    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner
    ])


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


    # initializing the count variables
    frame_count = 0


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

    # for testing purposes
    print('starting gaze frame grouping process')

    # looping through the frames
    while True:
        ret, image = cap.read()
        if ret == True:

            # initializing the variables
            # setting up the count variables
            head_front_count = 0
            head_up_right_count = 0
            head_up_left_count = 0
            head_down_right_count = 0
            head_down_left_count = 0
            face_count = 0
            detection_count = 0


            # prediction happens here
            # find the number of faces
            faces = find_faces(img, face_model)


            # iterate through each detected face
            for face in faces:

                # declaring boolean variables
                isLookingUp = False
                isLookingDown = False
                isLookingRight = False
                isLookingLeft = False
                isLookingFront = False


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
                    isLookingDown = True
                elif ang1 <= -THRESHOLD:
                    isLookingUp = True
                else:
                    isLookingFront = True

                # checking for angle 2
                if ang2 >= THRESHOLD:
                    isLookingRight = True
                elif ang2 <= -THRESHOLD:
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

                            print('frame group dict: ', frame_group_dict[frame_name])

                            frame_group_dict[frame_name]['upright_count'] += head_up_right_count
                            frame_group_dict[frame_name]['upleft_count'] += head_up_left_count
                            frame_group_dict[frame_name]['downright_count'] += head_down_right_count
                            frame_group_dict[frame_name]['downleft_count'] += head_down_left_count
                            frame_group_dict[frame_name]['front_count'] += head_front_count
                            frame_group_dict[frame_name]['detection_count'] += detection_count


            # for testing purposes
            print('gaze frame groupings count: ', frame_count)

            # increment the frame count
            frame_count += 1

        else:
            break


    # calculate the percentage values
    for key in frame_group_dict.keys():
        frame_group_details = frame_group_dict[key]
        frame_group_upright_count = frame_group_details['upright_count']
        frame_group_upleft_count = frame_group_details['upleft_count']
        frame_group_downright_count = frame_group_details['downright_count']
        frame_group_downleft_count = frame_group_details['downleft_count']
        frame_group_front_count = frame_group_details['front_count']

        print('detection count: ', frame_group_details['detection_count'])
        group_detection_count = 1 if frame_group_details['detection_count'] == 0 else frame_group_details['detection_count']



        frame_group_upright_perct = float(frame_group_upright_count / group_detection_count) * 100
        frame_group_upleft_perct = float(frame_group_upleft_count / group_detection_count) * 100
        frame_group_downright_perct = float(frame_group_downright_count / group_detection_count) * 100
        frame_group_downleft_perct = float(frame_group_downleft_count / group_detection_count) * 100
        frame_group_front_perct = float(frame_group_front_count / group_detection_count) * 100

        # assign the values to the same dictionary
        frame_group_dict[key]['upright_perct'] = round(frame_group_upright_perct, 1)
        frame_group_dict[key]['upleft_perct'] = round(frame_group_upleft_perct, 1)
        frame_group_dict[key]['downright_perct'] = round(frame_group_downright_perct, 1)
        frame_group_dict[key]['downleft_perct'] = round(frame_group_downleft_perct, 1)
        frame_group_dict[key]['front_perct'] = round(frame_group_front_perct, 1)

        # removing irrelevant items from the dictionary
        frame_group_dict[key].pop('upright_count')
        frame_group_dict[key].pop('upleft_count')
        frame_group_dict[key].pop('downright_count')
        frame_group_dict[key].pop('downleft_count')
        frame_group_dict[key].pop('front_count')
        frame_group_dict[key].pop('detection_count')


    # define the labels
    labels = ['upright_perct', 'upleft_perct', 'downright_perct', 'downleft_perct', 'front_perct']


    # for testing purposes
    print('ending gaze frame grouping process')

    # return the dictionary
    return frame_group_dict, labels


# this section will handle some database operations
def save_frame_detections(video_name):

    # for testing purposes
    print('starting the saving gaze frame recognition process')

    # retrieve the lecture emotion id
    lec_gaze = LectureGazeEstimation.objects.filter(lecture_video_id__video_name=video_name)
    lec_gaze_ser = LectureGazeEstimationSerializer(lec_gaze, many=True)
    lec_gaze_data = lec_gaze_ser.data[0]
    lec_gaze_id = lec_gaze_data['id']

    # create a new lecture activity frame detections id
    last_lec_gaze_frame_recognitions = LectureGazeFrameRecognitions.objects.order_by(
        'lecture_gaze_frame_recognition_id').last()
    new_lecture_gaze_frame_recognitions_id = "LGFR00001" if (
            last_lec_gaze_frame_recognitions is None) else \
        ig.generate_new_id(last_lec_gaze_frame_recognitions.lecture_gaze_frame_recognition_id)

    # calculate the frame detections
    frame_detections, frame_rate = get_lecture_gaze_estimation_for_frames(video_name)

    # to be added to the field 'frame_recognition_details' in the Lecture Gaze Frame Recordings
    frame_recognition_details = []

    # save the new lecture activity frame recognitions
    for detection in frame_detections:
        lec_gaze_frame_recognition_details = LectureGazeFrameRecognitionDetails()
        lec_gaze_frame_recognition_details.frame_name = detection['frame_name']
        lec_gaze_frame_recognition_details.upright_perct = detection['upright_perct']
        lec_gaze_frame_recognition_details.upleft_perct = detection['upleft_perct']
        lec_gaze_frame_recognition_details.downright_perct = detection['downright_perct']
        lec_gaze_frame_recognition_details.downleft_perct = detection['downleft_perct']
        lec_gaze_frame_recognition_details.front_perct = detection['front_perct']

        frame_recognition_details.append(lec_gaze_frame_recognition_details)

    lec_gaze_frame_recognitions = LectureGazeFrameRecognitions()
    lec_gaze_frame_recognitions.lecture_gaze_frame_recognition_id = new_lecture_gaze_frame_recognitions_id
    lec_gaze_frame_recognitions.lecture_gaze_id_id = lec_gaze_id
    lec_gaze_frame_recognitions.frame_recognition_details = frame_recognition_details

    lec_gaze_frame_recognitions.save()

    # for testing purposes
    print('ending the saving gaze frame recognition process')

    # now return the frame recognitions
    return frame_detections


# this method will save gaze frame groupings to the database
def save_frame_groupings(video_name, frame_landmarks, frame_group_dict):

    # for testing purposes
    print('starting the saving gaze frame groupings process')


    frame_group_percentages, gaze_labels = gaze_estimation_frame_groupings(video_name, frame_landmarks,
                                                                               frame_group_dict)

    # save the frame group details into db
    last_lec_gaze_frame_grouping = LectureGazeFrameGroupings.objects.order_by('lecture_gaze_frame_groupings_id').last()
    new_lecture_gaze_frame_grouping_id = "LGFG00001" if (last_lec_gaze_frame_grouping is None) else \
        ig.generate_new_id(last_lec_gaze_frame_grouping.lecture_gaze_frame_groupings_id)

    # retrieve the lecture activity id
    lec_gaze = LectureGazeEstimation.objects.filter(lecture_video_id__video_name=video_name)
    lec_gaze_ser = LectureGazeEstimationSerializer(lec_gaze, many=True)
    lec_gaze_id = lec_gaze_ser.data[0]['id']

    # create the frame group details
    frame_group_details = []

    for key in frame_group_percentages.keys():
        # create an object of type 'LectureActivityFrameGroupDetails'
        lec_gaze_frame_group_details = LectureGazeFrameGroupDetails()
        lec_gaze_frame_group_details.frame_group = key
        lec_gaze_frame_group_details.frame_group_percentages = frame_group_percentages[key]

        frame_group_details.append(lec_gaze_frame_group_details)

    new_lec_gaze_frame_groupings = LectureGazeFrameGroupings()
    new_lec_gaze_frame_groupings.lecture_gaze_frame_groupings_id = new_lecture_gaze_frame_grouping_id
    new_lec_gaze_frame_groupings.lecture_gaze_id_id = lec_gaze_id
    new_lec_gaze_frame_groupings.frame_group_details = frame_group_details

    # for testing purposes
    print('ending the saving gaze frame groupings process')

    # save
    new_lec_gaze_frame_groupings.save()


# this method will get gaze estimation correlations
def get_gaze_correlations(individual_lec_gaze, lec_recorded_activity_data):
    # this variable will be used to store the correlations
    correlations = []

    limit = 10

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(individual_lec_gaze))]

    # student gaze labels
    student_gaze_labels = ['Up and Right', 'Up and Left', 'Down and Right', 'Down and Left', 'Front']
    lecturer_activity_labels = ['seated', 'standing', 'walking']

    # lecturer recorded data list (lecturer)
    sitting_perct_list = []
    standing_perct_list = []
    walking_perct_list = []

    # lecture activity data list (student)
    upright_perct_list = []
    upleft_perct_list = []
    downright_perct_list = []
    downleft_perct_list = []
    front_perct_list = []

    # loop through the lecturer recorded data (lecturer)
    for data in lec_recorded_activity_data:
        sitting_perct_list.append(int(data['seated_count']))
        standing_perct_list.append(int(data['standing_count']))
        walking_perct_list.append(int(data['walking_count']))

    # loop through the lecturer recorded data (student)
    for data in individual_lec_gaze:
        upright_perct_list.append(int(data['looking_up_and_right_perct']))
        upleft_perct_list.append(int(data['looking_up_and_left_perct']))
        downright_perct_list.append(int(data['looking_down_and_right_perct']))
        downleft_perct_list.append(int(data['looking_down_and_left_perct']))
        front_perct_list.append(int(data['looking_front_perct']))

    corr_data = {'Up and Right': upright_perct_list, 'Up and Left': upleft_perct_list, 'Down and Right': downright_perct_list,
                 'Down and Left': downleft_perct_list, 'Front': front_perct_list,
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
        isStudentGaze = index[0] in student_gaze_labels
        # check whether the second index is a lecturer activity
        isLecturerAct = index[1] in lecturer_activity_labels

        # if both are student and lecturer activities, add to the dictionary
        if isStudentGaze & isLecturerAct:
            corr_dict['index'] = index
            corr_dict['value'] = pd_series.values[i]

            # append the dictionary to the 'correlations' list
            correlations.append(corr_dict)

    # return the list
    return correlations
