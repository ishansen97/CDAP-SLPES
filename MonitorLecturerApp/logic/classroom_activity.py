import tensorflow as tf
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
import os

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



