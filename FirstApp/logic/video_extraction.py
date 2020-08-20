import os
import cv2
import shutil

def VideoExtractor(request):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    video_name = request["video_name"]

    VIDEO_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\videos")
    VIDEO_PATH = os.path.join(VIDEO_DIR, video_name)

    # creating the new path to store extracted frames
    NEW_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\extracted\\{}".format(video_name))

    # check whether a specific directory exists
    if (os.path.isdir(NEW_DIR)):
        shutil.rmtree(NEW_DIR)

    # create the new directory
    os.mkdir(NEW_DIR)

    video = cv2.VideoCapture(VIDEO_PATH)

    no_of_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0


    while (frame_count < no_of_frames):

        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        new_file_name = "{}_frame_{}.png".format(video_name, frame_count)
        new_file_path = os.path.join(NEW_DIR, new_file_name)

        # save the extracted frames
        cv2.imwrite(new_file_path, gray)

        frame_count += 1


    # after extracting the frames, save the changes to static content
    p = os.popen("python manage.py collectstatic", "w")
    p.write("yes")

# retrieving the extracted frames for a given video
def getExtractedFrames(request):

    folder_name = request.get("folder_name")
    image_list = []

    print('folder name: ', folder_name)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXTRACTED_DIR = os.path.join(BASE_DIR, "assets\\FirstApp\\extracted\\{}".format(folder_name))

    # listing all the images in the directory
    for image in os.listdir(EXTRACTED_DIR):
        image_details = {"image": image}
        image_list.append(image_details)



    # checking for the number of frames
    if (len(image_list) > 0):
        return image_list

    else:
        return "No extracted frames were found"