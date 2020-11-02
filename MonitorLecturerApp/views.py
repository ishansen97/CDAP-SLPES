from django.shortcuts import render, redirect
from  django.http import HttpResponse
from django.conf.urls import url
from rest_framework import routers
from rest_framework.views import APIView
from rest_framework.response import Response

from LectureSummarizingApp.models import LectureAudio
from LectureSummarizingApp.serializer import LectureAudioSerializer
from . import views
from .models import *
from . serializers import *

import cv2
import os
import datetime
from datetime import datetime as dt



# Create your views here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TeachersList(APIView):

    def get(self, request):
        teachers = RegisterTeacher.objects.all()
        serializer = RegisterTeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    def post(self):
        pass

def index (request):
    return render(request, 'MonitorLecturerApp/index.html')

# def hello (request):
#     return render(request, 'MonitorLecturerApp/beginer.html')

def startup (request) :
    return render(request, '')

def hello(request):
    # page = '<h1>THIS IS MY HOME</h1>' + '<h2> Hello Ishan</h2>' + '<button>Click Me</button>'

    try:

        admin = request.session['admin']

        obj = {'Message': 'Student and Lecturer Performance Enhancement System'}
        folder = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\lecturer_videos'))
        videoPaths = [os.path.join(folder, file) for file in os.listdir(folder)]
        videos = []
        durations = []

        # retrieve audio details from db
        lecture_audio = LectureAudio.objects.all()
        lec_audio_serializer = LectureAudioSerializer(lecture_audio, many=True)
        lec_audio_data = lec_audio_serializer.data

        lec_list = []

        for audio in lec_audio_data:
            lec_audio_object = {}
            lec_audio_object["id"] = audio["id"]
            lec_audio_object["date"] = audio["lecturer_date"]
            lec_audio_object["subject"] = audio["subject"]["name"]
            lec_audio_object["lecturer"] = audio["lecturer"]["fname"] + " " + audio["lecturer"]["lname"]
            lec_audio_object["lecturer_id"] = audio["lecturer"]["id"]

            # append to the list
            lec_list.append(lec_audio_object)

        # the list needs to be sorted by the date
        lec_list.sort(key=lambda date: dt.strptime(str(date['date']), "%Y-%m-%d"), reverse=True)

        # retrieve exsiting lecture recorded videos
        lec_video_meta = LecturerVideoMetaData.objects.all()
        lec_video_meta_ser = LecturerVideoMetaDataSerializer(lec_video_meta, many=True)
        lec_video_meta_data = lec_video_meta_ser.data

        for videoPath in videoPaths:
            video = LecturerVideo()
            video = {}
            cap = cv2.VideoCapture(videoPath)
            fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = int(frame_count / fps)
            durations.append(duration)
            videoName = os.path.basename(videoPath)
            # videoName = videos.append(os.path.basename(videoPath))
            durationObj = datetime.timedelta(seconds=duration)
            video['path'] = videoPath
            video['name'] = videoName
            video['duration'] = str(durationObj)
            video['video_id'] = None

            # checking whether this video already exists
            for recorded_lecture in lec_video_meta_data:

                print('recorded lecture: ', recorded_lecture)

                if videoName == recorded_lecture['lecturer_video_id']['lecture_video_name']:
                    video['isAvailable'] = True
                    video['video_id'] = recorded_lecture['lecturer_video_id']['id']


            videos.append(video)
            print('Video Name: ', video['name'])
        context = {'object': obj, 'Videos': videos, 'durations': durations, 'template_name': 'MonitorLecturerApp/template.html', 'lec_list': lec_list}
        return render(request, 'MonitorLecturerApp/index.html', context)

    # in case the 'admin' session is not there
    except KeyError as exc:
        return redirect('/401')

    # in case of general exceptions
    except Exception as exc:
        print('exception: ', exc)
        return redirect('/500')


def view404(request):
    return render(request, 'MonitorLecturerApp/404.html')

def blank(request):
    return render(request, 'MonitorLecturerApp/blank.html')

def buttons(request):
    return render(request, 'MonitorLecturerApp/buttons.html')

def cards(request):
    return render(request, 'MonitorLecturerApp/cards.html')

def charts(request):
    return render(request, 'MonitorLecturerApp/charts.html')

def forget_password(request):
    return render(request, 'MonitorLecturerApp/forgot-password.html')

def login(request):
    return render(request, 'MonitorLecturerApp/login.html')

def register(request):
    return render(request, 'MonitorLecturerApp/register.html')


def template(request):
    obj = {'Message': 'Student and Lecturer Performance Enhancement System'}
    return render(request, 'MonitorLecturerApp/template.html', {'template_name': 'MonitorLecturerApp/template.html', 'object': obj})

def base(request):
    return render(request, 'MonitorLecturerApp/base.html')

def child(request):
    return render(request, 'MonitorLecturerApp/child.html', {'template_name': 'MonitorLecturerApp/base.html'})

def lecVideo(request):
    video = "poses.mp4"
    obj = {'Message': 'Student and Lecturer Performance Enhancement System'}
    folder = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\lecturer_videos'))
    videoPaths = [os.path.join(folder, file) for file in os.listdir(folder)]
    videos = []
    durations = []

    for videoPath in videoPaths:
        video = LecturerVideo()
        cap = cv2.VideoCapture(videoPath)
        fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(frame_count / fps)
        durations.append(duration)
        videoName = os.path.basename(videoPath)
        # videoName = videos.append(os.path.basename(videoPath))
        durationObj = datetime.timedelta(seconds=duration)
        video.path = videoPath
        video.name = videoName
        video.duration = str(durationObj)
        videos.append(video)
        print('Video Name: ', video.name)

        # audio =
    context = {'object': obj, 'Videos': videos, 'durations': durations, 'template_name': 'MonitorLecturerApp/template.html', 'video_name': video}
    return render(request, 'MonitorLecturerApp/lecVideo.html', context)

    # for  audioPath in audiopaths:
    #     audio = tAudio()


def testFrameRecognitions(request):
    return render(request, "MonitorLecturerApp/test_frame_recognitions.html")