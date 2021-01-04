
import urllib3
import urllib.request as req
import cv2
import numpy as np
import time

isStop = 0


def IPWebcamTest():

    # Replace the URL with your own IPwebcam shot.jpg IP:port
    # url = 'http://192.168.2.35:8080/shot.jpg'
    url = 'http://192.168.8.103:8080/shot.jpg'
    # url = 'http://192.168.1.11:8080/startvideo?force=1&tag=rec'
    # url = 'http://192.168.1.11:8080/stopvideo?force=1'

    size = (600, 600)

    vid_cod = cv2.VideoWriter_fourcc(*'XVID')
    # vid_cod = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    # output = cv2.VideoWriter("cam_video.avi", vid_cod, 20.0, (640, 480))
    # output = cv2.VideoWriter("cam_video.mp4", vid_cod, 20.0, size)
    output = cv2.VideoWriter("cam_video.mp4", vid_cod, 10.0, size)

    no_of_frames = 0

    while True:
        # Use urllib to get the image from the IP camera
        imgResp = req.urlopen(url)
        # imgResp = urllib3.respon

        # Numpy to convert into a array
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)

        # Finally decode the array to OpenCV usable format ;)
        img = cv2.imdecode(imgNp, -1)
        # resize the image
        img = cv2.resize(img, (600, 600))

        # put the image on screen
        # cv2.imshow('IPWebcam', img)

        # write to the output writer
        output.write(img)

        # To give the processor some less stress
        # time.sleep(0.1)
        # time.sleep(1)

        no_of_frames += 1
        if isStop == 1:
            break

    # imgResp.release()
    # cv2.destroyAllWindows()
    print('no of frames: ', no_of_frames)