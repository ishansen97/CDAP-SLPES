import tensorflow as tf
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
import os

from FirstApp.logic.custom_sorter import custom_object_sorter
from FirstApp.logic.id_generator import generate_new_id
from MonitorLecturerApp.models import LecturerVideoMetaData, LecturerActivityFrameRecognitions, \
    LecturerActivityFrameRecognitionDetails
from MonitorLecturerApp.serializers import LecturerVideoMetaDataSerializer


def activity_recognition(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "MonitorLecturerApp\\models")
    # VIDEO_PATH = os.path.join(BASE_DIR, "assets\\FirstApp\\lecturer_videos\\{}".format(video_name)) -> Uncomment after integration
    VIDEO_PATH = os.path.join(BASE_DIR, "static\\FirstApp\\lecturer_videos\\{}".format(video_name))

    print('video name: ', video_name)

    # detector_path = os.path.join(CLASSIFIER_DIR, "keras_model.h5")

    detector_path = os.path.join(CLASSIFIER_DIR, "keras_model_updated.h5")


    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    class_labels = ['Seated Teaching', 'Teaching by Standing', 'Teaching by Walking']


    # img = cv2.imread('test2.jpg')

    # Load the model
    model = tensorflow.keras.models.load_model(detector_path)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])


    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    # "C://Users//DELL//Downloads//Classroom_Video.mp4"
    video1 = 'E:\\Studies\\SLIIT\\4th Year\\Python Projects\\classroom activity models\\videos\\{}'.format(video_name)
    video = cv2.VideoCapture(VIDEO_PATH)
    # additional
    # getting the frames per second (fps)
    # fps = video.get(cv2.CAP_PROP_FPS)

    # getting the number of frames using CAP_PROP_FRAME_COUNT method
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_count = 0
    seated_count = 0.0
    standing_count = 0.0
    walking_count = 0.0

    # while loop is conditioned like this to avoid the termination of the loop with an exception
    while (frame_count < no_of_frames):

        cap, frame = video.read()
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(frame, size)
        # image_array = np.asarray(img)
        normalized_image_array = (img.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = model.predict(data)
        label = class_labels[prediction.argmax()]

        if (label == class_labels[0]):
            seated_count += 1
        elif (label == class_labels[1]):
            standing_count += 1
        elif (label == class_labels[2]):
            walking_count += 1
        # text = label + format(prediction[prediction.argmax()])

        # if label:
        cv2.putText(frame, label, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        # else:
        #     cv2.putText(frame, 'Unknown', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        frame_count += 1
        # cv2.imshow('Activity Recognition', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cv2.destroyAllWindows()
    print("No of frames: ", frame_count)
    print("No of frames in seated_count: ", seated_count)
    print("No of frames in standing_count: ", standing_count)
    print("No of frames in walking_count: ", walking_count)

    # calculating the percentages
    sit_perct = (seated_count / no_of_frames) * 100

    stand_perct = (standing_count / no_of_frames) * 100

    walk_perct = (walking_count / no_of_frames) * 100

    return {
        "sitting_perct": sit_perct,
        "standing_perct": stand_perct,
        "walking_perct": walk_perct
    }



# this method will calculated lecturer activity for frames
def get_lecturer_activity_for_frames(video_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\lecturer_videos\\{}".format(video_name))
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_02.h5")
    # CLASSIFIER_DIR = os.path.join(BASE_DIR, "FirstApp\\classifiers\\student_activity_version_03.h5")
    CLASSIFIER_DIR = os.path.join(BASE_DIR, "MonitorLecturerApp\\models")
    CLASSIFIER_PATH = os.path.join(CLASSIFIER_DIR, "keras_model_updated.h5")


    # load our serialized persosn detection model from disk
    print("[INFO] loading model...")


    np.set_printoptions(suppress=True)


    class_labels = ['Seated Teaching', 'Teaching by Standing', 'Teaching by Walking']

    model = tensorflow.keras.models.load_model(CLASSIFIER_PATH)
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)

    # iteration
    video = cv2.VideoCapture(VIDEO_DIR)
    no_of_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)

    print('fps: ', fps)
    frame_count = 0

    # frame activity recognitions
    frame_activity_recognitions = []

    # for testing purposes
    print('starting the frame activity recognition process')

    # looping through the frames
    while (frame_count < no_of_frames):


        # define the count variables for each frame
        sitting_count = 0
        standing_count = 0
        walking_count = 0

        ret, image = video.read()

        # derive the frame name
        frame_name = "frame-{}".format(frame_count)

        frame_details = {}
        frame_details['frame_name'] = frame_name


        detection = cv2.resize(image, size)

        image_array = np.asarray(detection)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = model.predict(data)

        label = class_labels[prediction.argmax()]

        # increment the relevant count, based on the label
        if (label == class_labels[0]):
            sitting_count += 1
        elif (label == class_labels[1]):
            standing_count += 1
        elif (label == class_labels[2]):
            walking_count += 1



        print('current frame: ', frame_count)
        # increment frame count
        frame_count += 1


        # calculating the percentages for the frame
        sitting_perct = float(sitting_count) * 100
        standing_perct = float(standing_count) * 100
        walking_perct = float(walking_count) * 100

        # adding the percentage values to the frame details
        frame_details['sitting_perct'] = sitting_perct
        frame_details['standing_perct'] = standing_perct
        frame_details['walking_perct'] = walking_perct

        # push to all the frame details
        frame_activity_recognitions.append(frame_details)




    # sort the recognitions based on the frame number
    sorted_activity_frame_recognitions = custom_object_sorter(frame_activity_recognitions)

    # for testing purposes
    print('ending the frame activity recognition process')

    # return the detected frame percentages
    return sorted_activity_frame_recognitions, fps


# this section will handle saving activity entities to the database
def save_frame_recognition(video_name):

    # for testing purposes
    print('starting the saving activity frame recognition process')

    # retrieve the lecture activity id
    lec_activity = LecturerVideoMetaData.objects.filter(lecturer_video_id__lecture_video_name=video_name)
    lec_activity_ser = LecturerVideoMetaDataSerializer(lec_activity, many=True)
    lec_activity_data = lec_activity_ser.data[0]
    lec_activity_id = lec_activity_data['id']

    # create a new lecture activity frame detections id
    last_lec_activity_frame_recognitions = LecturerActivityFrameRecognitions.objects.order_by(
        'lecturer_activity_frame_recognition_id').last()
    new_lecture_activity_frame_recognitions_id = "LLAFR00001" if (last_lec_activity_frame_recognitions is None) else \
        generate_new_id(last_lec_activity_frame_recognitions.lecturer_activity_frame_recognition_id)

    # calculate the frame detections
    frame_detections, fps = get_lecturer_activity_for_frames(video_name)

    frame_recognition_details = []

    # save the new lecture activity frame recognitions
    for detection in frame_detections:
        lec_activity_frame_recognition_details = LecturerActivityFrameRecognitionDetails()
        lec_activity_frame_recognition_details.frame_name = detection['frame_name']
        lec_activity_frame_recognition_details.sitting_perct = detection['sitting_perct']
        lec_activity_frame_recognition_details.standing_perct = detection['standing_perct']
        lec_activity_frame_recognition_details.walking_perct = detection['walking_perct']

        frame_recognition_details.append(lec_activity_frame_recognition_details)

    lec_activity_frame_recognitions = LecturerActivityFrameRecognitions()
    lec_activity_frame_recognitions.lecturer_activity_frame_recognition_id = new_lecture_activity_frame_recognitions_id
    lec_activity_frame_recognitions.lecturer_meta_id_id = lec_activity_id
    lec_activity_frame_recognitions.frame_recognition_details = frame_recognition_details
    lec_activity_frame_recognitions.fps = float(fps)

    lec_activity_frame_recognitions.save()

    # for testing purposes
    print('ending the saving activity frame recognition process')

    # now return the frame detections
    return frame_detections, fps
