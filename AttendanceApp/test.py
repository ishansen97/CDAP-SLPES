import json

import requests
import urllib3
import urllib.request as req
import cv2
import numpy as np
import time
import os
import time
from threading import *
import face_recognition

from AttendanceApp.models import Student, Attendance
from FirstApp.MongoModels import Subject
from FirstApp.logic.id_generator import generate_new_id

isStop = 0
firstIteration = 0

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
def videoDir(name):
    VIDEO_DIR = os.path.join(BASE_DIR, "static\\FirstApp\\videos\\{}".format(name))
    return VIDEO_DIR


def imageDir(name):
    IMAGE_DIR = os.path.join(BASE_DIR, "AttendanceApp\\unknown\\{}".format(name))
    return IMAGE_DIR

def saveImage(img, name, subjectCode, date, subjectId, lecturerId):
    cv2.imwrite(imageDir(name + '.png'), img)
    knownEncodings = []
    knownNames = []
    actualKnownNames = []
    knownDir = os.path.join(BASE_DIR, "AttendanceApp\\known")
    unknownDir = os.path.join(BASE_DIR, "AttendanceApp\\unknown")
    knownDir = knownDir.replace('\\', '/')
    unknownDir = unknownDir.replace('\\', '/')

    for file in os.listdir(knownDir):
        image = resizeImage(knownDir + '/' + file)
        img_encodings = face_recognition.face_encodings(image)[0]
        knownEncodings.append(img_encodings)
        knownNames.append(file.split('.')[0])

    attendance = []

    for file in os.listdir(unknownDir):
        print('processing ' + file)
        image = resizeImage(unknownDir + '/' + file)
        img_encodings = face_recognition.face_encodings(image)
        print(face_recognition.face_encodings(image))
        if not len(img_encodings):
            print('cannot find encodeings for ' + file)
            continue
        img_encodings = face_recognition.face_encodings(image)[0]
        results = face_recognition.compare_faces(knownEncodings, img_encodings)
        print(results)
        for i in range(len(results)):
            if results[i]:
                attendance.append(knownNames[i].split('(')[0])
    print(list(set(attendance)))
    saveAttendanceToDB(list(set(attendance)), subjectCode, date)


def startProcessing(lecturerId, subejectId, subjectCode):

    content = {
        'lecturer': lecturerId,
        'subject': subejectId,
        'subject_code': subjectCode,
        'video_length': '00:20:00'
    }

    json_content = json.dumps(content)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post('http://127.0.0.1:8000/automation-process/', data=json_content, headers=headers)

    return response

def saveAttendanceToDB(students, subjectCode, date):

    subject = Subject.objects.filter(subject_code=subjectCode)
    allStudents = Student.objects.all()

    for aS in allStudents:
        for s in students:
            if s == aS.studentId:
                prev_attendance = Attendance.objects.order_by('attendanceID').last()
                newAttendanceId = "SA00001" if prev_attendance is None else generate_new_id(
                    prev_attendance.attendanceID)
                Attendance(
                    attendanceID=newAttendanceId,
                    student=aS,
                    subject=subject[0],
                    date=date,
                    attendance=True,
                    feedback=''
                ).save()
            else:
                prev_attendance = Attendance.objects.order_by('attendanceID').last()
                newAttendanceId = "SA00001" if prev_attendance is None else generate_new_id(
                    prev_attendance.attendanceID)
                Attendance(
                    attendanceID=newAttendanceId,
                    student=aS,
                    subject=subject[0],
                    date=date,
                    attendance=False,
                    feedback=''
                ).save()



def resizeImage(img):
    img = cv2.imread(img)
    (h, w) = img.shape[:2]
    width = 600
    ratio = width / float(w)
    height = int(h * ratio)
    return cv2.resize(img, (width ,height))

def startThread(img, name, subject, date, subjectId, lecturerId):
    t = Thread(saveImage(img, name, subject, date, subjectId, lecturerId))
    time.sleep(2)
    t.start()

def IPWebcamTest(params):

    # Replace the URL with your own IPwebcam shot.jpg IP:port
    # url = 'http://192.168.2.35:8080/shot.jpg'
    # url = 'http://192.168.137.209:8080/shot.jpg'
    url = 'http://192.168.8.101:8080/shot.jpg'
    # url = 'http://192.168.1.11:8080/startvideo?force=1&tag=rec'
    # url = 'http://192.168.1.11:8080/stopvideo?force=1'

    size = (600, 600)

    video_name = params['dateFormat'] + "_" + params['subject_code'] + "_student_video.mp4"
    attendanceCaptureName = params['dateFormat'] + "_" + params['subject_code'] + "_student_video"
    subject_id = params['subject_id']
    lecturer_id = params['lecturerId']
    subject_code = params['subject_code']
    print('video name: ', video_name)


    vid_cod = cv2.VideoWriter_fourcc(*'mp4v')
    # vid_cod = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    # output = cv2.VideoWriter("cam_video.avi", vid_cod, 20.0, (640, 480))
    # output = cv2.VideoWriter("cam_video.mp4", vid_cod, 20.0, size)
    output = cv2.VideoWriter(videoDir(video_name), vid_cod, 10.0, size)

    no_of_frames = 0
    firstIteration = 0

    while True:
        # Use urllib to get the image from the IP camera
        imgResp = req.urlopen(url)
        # imgResp = urllib3.respon

        # Numpy to convert into a array
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)

        # Finally decode the array to OpenCV usable format ;)
        img = cv2.imdecode(imgNp, -1)
        if firstIteration == 0:
            startThread(img, attendanceCaptureName + '(1)', params['subject_code'], params['dateFormat'], subject_id, lecturer_id)
            firstIteration = 1
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
            print('stopping')
            break

    # after saving the video, save the changes to static content
    p = os.popen("python manage.py collectstatic", "w")
    p.write("yes")
    startProcessing(lecturer_id, subject_id, subject_code)
    # imgResp.release()
    # cv2.destroyAllWindows()
    print('no of frames: ', no_of_frames)