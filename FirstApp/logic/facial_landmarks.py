from imutils import face_utils
import os
import cv2
import dlib
import numpy as np
import imutils


def get2DPoints(image):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers")

    detector_path = os.path.join(CLASSIFIER_DIR, "shape_predictor_68_face_landmarks.dat")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(detector_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale image
    rects = detector(gray, 1)

    left_corner_arr = None
    right_corner_arr = None
    nose_tip_arr = None
    right_mouth_arr = None
    left_mouth_arr = None
    chin_arr = None
    face_center_arr = None
    face_center_top_arr = None
    face_center_bottom_arr = None
    count = 0

    print('no of faces: ', len(rects))

    if (len(rects)):
        left_corner_arr = np.zeros((len(rects), 2))
        right_corner_arr = np.zeros((len(rects), 2))
        nose_tip_arr = np.zeros((len(rects), 2))
        right_mouth_arr = np.zeros((len(rects), 2))
        left_mouth_arr = np.zeros((len(rects), 2))
        chin_arr = np.zeros((len(rects), 2))
        face_center_top_arr = np.zeros((len(rects), 2))
        face_center_bottom_arr = np.zeros((len(rects), 2))


        for (i, rect) in enumerate(rects):

            left_corner = None
            right_corner = None
            nose_tip = None
            right_mouth = None
            left_mouth = None
            chin = None


            (fx, fy, fw, fh) = face_utils.rect_to_bb(rect)
            cv2.rectangle(image, (fx, fy), (fx+fw, fy+fh), (0, 255, 0), 2)
            face_center_top = [int(fx + fw/2), int(fy)]
            face_center_bottom = [int(fx + fw/2), int(fy + fh)]
            cv2.line(image, (int(fx + fw/2), int(fy)), (int(fx + fw/2), int(fy + fh)), (0, 255, 0), 2)

            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # looping through each facial landmark category
            for (name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                # clone the original image so we can draw on it, then
                # display the name of the face part on the image
                clone = image

                # loop over the subset of facial landmarks, drawing the
                # specific face part

                for (x, y) in shape[i:j]:
                    if (name == 'left_eye'):
                        # maxArr = np.amax(shape[i:j], axis=0)
                        # minArr = np.amin(shape[i:j], axis=0)
                        left_corner = np.amax(shape[i:j], axis=0)

                    elif (name == 'right_eye'):
                        # maxArr = np.amax(shape[i:j], axis=0)
                        # minArr = np.amin(shape[i:j], axis=0)
                        right_corner = np.amin(shape[i:j], axis=0)

                    elif (name == 'jaw'):
                        minArr = np.array(shape[i:j][8], dtype=int)
                        chin = np.array(shape[i:j][8], dtype=int)

                        # cv2.putText(clone, "Chin", (int(minArr[0]), int(minArr[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.circle(image, (int(minArr[0]), int(minArr[1])), 3, (255, 0, 255), -1)
                        # cv2.circle(clone, (int(minArr[0]), int(minArr[1])), 3, (0, 255, 255), -1)

                    elif (name == 'nose'):
                        # nose_tip = np.array(shape[i:j][3], dtype=int)
                        nose_tip = np.array(shape[i:j][3], dtype=int)
                        # cv2.putText(clone, "Nose tip", (int(nose_tip[0]), int(nose_tip[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                        #             2)
                        # cv2.circle(clone, (int(nose_tip[0]), int(nose_tip[1])), 3, (255, 0, 255), -1)

                    elif (name == 'inner_mouth'):
                        # maxArr = np.amax(shape[i:j], axis=0)
                        # minArr = np.amin(shape[i:j], axis=0)
                        right_mouth = np.amin(shape[i:j], axis=0)
                        left_mouth = np.amax(shape[i:j], axis=0)
                        # cv2.circle(clone, (maxArr[0], maxArr[1]), 3, (127, 0, 255), -1)
                        # cv2.circle(clone, (minArr[0], minArr[1]), 3, (127, 0, 255), -1)

                    # else:
                    # cv2.circle(image, (x, y), 3, (255, 0, 255), -1)

            left_corner_arr[count] = left_corner
            right_corner_arr[count] = right_corner
            nose_tip_arr[count] = nose_tip
            right_mouth_arr[count] = right_mouth
            left_mouth_arr[count] = left_mouth
            chin_arr[count] = chin
            face_center_top_arr[count] = face_center_top
            face_center_bottom_arr[count] = face_center_bottom

            count += 1



    return left_corner_arr, right_corner_arr, nose_tip_arr, right_mouth_arr, left_mouth_arr, chin_arr, face_center_top_arr, face_center_bottom_arr, count

            # extract the ROI of the face region as a separate image
        #     (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
        #     roi = image[y:y + h, x:x + w]
        #     roi = imutils.resize(roi, width=250, inter=cv2.INTER_CUBIC)
        #
        #     # show the particular face part
        #     cv2.imshow("ROI", roi)
        #     cv2.imshow("Image", clone)
        #     cv2.waitKey(0)
        #
        #     # visualize all facial landmarks with a transparent overlay
        # output = face_utils.visualize_facial_landmarks(image, shape)
        # cv2.imshow("Image", output)
        # cv2.waitKey(0)