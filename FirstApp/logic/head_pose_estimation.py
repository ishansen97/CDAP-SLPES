
import os
import cv2
import numpy as np
import shutil
from .facial_landmarks import get2DPoints
from .classes import pose
# Read Image


def estimatePose(request):


    directory = request['directory']
    images = request['images']

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IMAGE_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\images")
    SPEC_DIR = os.path.join(IMAGE_DIR, "{}".format(directory))

    # new directory will be created to store pose estimations
    new_dir_name = "static\\FirstApp\\poses\\{}".format(directory)
    new_dir = os.path.join(BASE_DIR, new_dir_name)
    face_count_response = 0
    pose_response_list = []

    if (os.path.isdir(new_dir)):
        # delete the previous directory
        shutil.rmtree(new_dir)

    # create the new directory
    os.mkdir(new_dir)

    for im in images:

        IMAGE_PATH = os.path.join(SPEC_DIR, "{}".format(im))
        image = cv2.imread(IMAGE_PATH)
        size = image.shape

        left_corner, right_corner, nose_tip, right_mouth, left_mouth, chin, face_center_top, face_center_bottom, face_count = get2DPoints(image)

        # if faces are found
        if left_corner is not None:


            # 3D model points.
            model_points = np.array([
                (0.0, 0.0, 0.0),  # Nose tip
                (0.0, -330.0, -65.0),  # Chin
                (-225.0, 170.0, -135.0),  # Left eye left corner
                (225.0, 170.0, -135.0),  # Right eye right corne
                (-150.0, -150.0, -125.0),  # Left Mouth corner
                (150.0, -150.0, -125.0)  # Right mouth corner

            ])

            # Camera internals

            focal_length = size[1]
            center = (size[1] / 2, size[0] / 2)
            camera_matrix = np.array(
                [[focal_length, 0, center[0]],
                 [0, focal_length, center[1]],
                 [0, 0, 1]], dtype="double"
            )

            # print("Camera Matrix :\n {0}".format(camera_matrix))

            for i in range (face_count):

                text = ''
                # 2D image points. If you change the image, you need to change vector
                image_points = np.array([
                    nose_tip[i],
                    chin[i],
                    left_corner[i],
                    right_corner[i],
                    left_mouth[i],
                    right_mouth[i]
                ], dtype="double")


                dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
                (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs,
                                                                              flags=cv2.SOLVEPNP_ITERATIVE)


                # Project a 3D point (0, 0, 1000.0) onto the image plane.
                # We use this to draw a line sticking out of the nose


                (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector,
                                                                 camera_matrix, dist_coeffs)

                # for p in image_points:
                #     cv2.circle(im, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

                p1 = (int(image_points[0][0]), int(image_points[0][1]))
                p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

                if (p2[0] < face_center_top[i][0]):
                    text = 'RIGHT'
                else:
                    text = 'LEFT'

                cv2.putText(image, text, p2, cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                cv2.line(image, p1, p2, (255, 0, 0), 2)

                # saving the image
                new_file = os.path.join(new_dir, im)

                cv2.imwrite(new_file, image)

                face_count_response += 1

                # create a response object for the image
                pose_response = {}
                pose_response["directory"] = directory
                pose_response["image"] = im
                pose_response["label"] = text

                pose_response_list.append(pose_response)





        else:
            print('No faces found')


    # respond 'yes' to the command line prompt
    p = os.popen('python manage.py collectstatic', "w")
    p.write("yes")

    # returning the static path
    STATIC_POSE = os.path.join(BASE_DIR, "assets\\FirstApp\\pose")
    STATIC_SPEC = os.path.join(STATIC_POSE, "{}".format(directory))

    # if no images were created
    if (face_count_response < 1):
        shutil.rmtree(new_dir)
        return "No faces were found"

    return pose_response_list