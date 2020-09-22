from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from . models import Teachers, Video, VideoMeta, RegisterUser
from . MongoModels import *
from . serializers import *
from . emotion_detector import detect_emotion
from . ImageOperations import saveImage
from . logic import head_pose_estimation
from . logic import video_extraction
from . forms import *
import cv2
import os
import datetime


# hashing
from django.contrib.auth.hashers import make_password

# Create your views here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class teachersList(APIView):

    def get(self, request):
        teachers = Teachers.objects.all()
        serializer = TeachersSerializer(teachers, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class RegisterViewSet(viewsets.ModelViewSet):

    queryset = RegisterUser.objects.all().order_by('firstName')
    serializer_class = RegisterUserSerializer


# to create images
class ImageViewSet(APIView):

    def post(self, request):
        saveImage(request.data)
        return Response({"response": "successful"})


# to perform pose estimation on images
class GazeEstimationViewSet(APIView):

    def post(self, request):
        response = head_pose_estimation.estimatePose(request.data)
        return Response({"response": response})


# to perform video extraction
class VideoExtractionViewSet(APIView):

    def get(self, request):
        response = video_extraction.getExtractedFrames(request.query_params)
        return Response({"response": response})

    def post(self, request):
        response = video_extraction.VideoExtractor(request.data)
        return Response({"response": response})

# lecture emotions view set
class LectureEmotionViewSet(APIView):

    def get(self, request):
        emotions = LectureEmotionReport.objects.all().order_by('lecture_id')
        serializer = LectureEmotionSerializer(emotions, many=True)
        return Response({"response": serializer.data})

    def post(self, request):
        LectureEmotionReport(
            lecture_id=request.data["lecture_id"],
            happy_perct=request.data["happy_perct"],
            sad_perct=request.data["sad_perct"],
            angry_perct=request.data["angry_perct"],
            surprise_perct=request.data["surprise_perct"],
            disgust_perct=request.data["disgust_perct"],
            neutral_perct=request.data["neutral_perct"]
        ).save()
        return Response({"response": request.data})


class LectureViewSet(APIView):

    def get(self, request):
        lectures = Lecture.objects.all().order_by('date')
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data)

    def post(self, request):
        Lecture(
            lecture_id=request.data['lecture_id']
        ).save()
        return Response({"response": request})


####### VIEWS ######
@login_required(login_url='/login')
def hello(request):

    username = request.user.username
    obj = {'Message': 'Student and Lecturer Performance Enhancement System', 'username': username}
    folder = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\videos'))
    videoPaths = [os.path.join(folder, file) for file in os.listdir(folder)]
    videos = []
    durations = []

    for videoPath in videoPaths:
        video = Video()
        cap = cv2.VideoCapture(videoPath)
        fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(frame_count / fps)
        durations.append(duration)
        videoName = os.path.basename(videoPath)
        videoName = os.path.basename(videoPath)
        # videoName = videos.append(os.path.basename(videoPath))
        durationObj = datetime.timedelta(seconds=duration)
        video.path = videoPath
        video.name = videoName
        video.duration = str(durationObj)
        videos.append(video)
    context = {'object': obj, 'Videos': videos, 'durations': durations, 'template_name': 'FirstApp/template.html'}
    return render(request, 'FirstApp/Home.html', context)

def view404(request):
    return render(request, 'FirstApp/404.html')

# querying the database
def blank(request):
    emotions = LectureEmotionReport.objects.all().order_by('lecture_id')
    return render(request, 'FirstApp/blank.html', {'details': emotions})

@login_required(login_url='/login')
def gaze(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    except Exception as exc:
        return redirect('/500')

    return render(request, "FirstApp/gaze.html",
                  {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})


# to redirect to the gaze interface
def processGaze(request):
    print('My name is Ishan')
    images = request.session.get('images', default='')
    imageList = images.split(',')

    for i in imageList:
        print(i)
    return redirect('/')


# the corresponding view for pose estimation
@login_required(login_url='/login')
def pose(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    except Exception as exc:
        return redirect('/500')

    return render(request, "FirstApp/pose.html",
                  {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})

def charts(request):
    return render(request, 'FirstApp/charts.html')

def forget_password(request):
    return render(request, 'FirstApp/forgot-password.html')

def loginForm(request):
    return render(request, 'FirstApp/login.html')

def register(request):
    return render(request, 'FirstApp/register.html')

def webcam(request):
    video = cv2.VideoCapture(os.path.join(BASE_DIR, 'static//FirstApp//videos//Classroom_video.mp4'))

    while (True):
        cap, frame = video.read()

        cv2.imshow("Frame", frame)

        if (cv2.waitKey(1) & 0XFF == ord('q')):
            break

    video.release()
    cv2.destroyAllWindows()
    # video = cv2.imread('D://SLIIT/Year 4//Sample Projects//django_project//DemoProject//static//FirstApp/videos/Classroom_video.mp4')

    return redirect('/')

# to process video for emotion detection
@login_required(login_url='/login')
def video(request):
    title = 'Student and Lecturer Performance Enhancement System'
    video_name = request.GET.get('video_name')
    video_url = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\videos\\{0}'.format(video_name)))
    meta_data = detect_emotion(video_url)
    # meta_data = VideoMeta()
    # calculating the respective percentages
    meta_data.calcPercentages()
    context = {'title': title, 'video_name': video_name, 'url': video_url, 'meta': meta_data}

    return render(request, 'FirstApp/video.html', context)


# extractor view
@login_required(login_url='/login')
def extractor(request):
    folder = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\videos'))
    videoPaths = [os.path.join(folder, file) for file in os.listdir(folder)]
    videos = []
    durations = []

    # setting up the first video details
    first_video_path = videoPaths[0]
    first_video = Video()
    cap = cv2.VideoCapture(first_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(frame_count / fps)
    videoName = os.path.basename(first_video_path)
    durationObj = datetime.timedelta(seconds=duration)
    first_video.path = first_video_path
    first_video.name = videoName
    first_video.duration = str(durationObj)


    for videoPath in videoPaths:
        video = Video()
        cap = cv2.VideoCapture(videoPath)
        fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(frame_count / fps)
        durations.append(duration)
        videoName = os.path.basename(videoPath)
        durationObj = datetime.timedelta(seconds=duration)
        video.path = videoPath
        video.name = videoName
        video.duration = str(durationObj)
        videos.append(video)
    context = {'Videos': videos, 'firstVideo': first_video, 'durations': durations, 'template_name': 'FirstApp/template.html'}
    return render(request, 'FirstApp/extractor.html', context)

def template(request):
    obj = {'Message': 'Student and Lecturer Performance Enhancement System'}
    return render(request, 'FirstApp/template.html', {'template_name': 'FirstApp/template.html', 'object': obj})

def base(request):
    return render(request, 'FirstApp/base.html')

def child(request):
    return render(request, 'FirstApp/child.html', {'template_name': 'FirstApp/base.html'})

# displaying video results
@login_required(login_url='/login')
def video_result(request):

    try:
        # retrieving data from the db
        lecturer = request.session['lecturer']

        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)




        folder = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\videos'))
        videoPaths = [os.path.join(folder, file) for file in os.listdir(folder)]
        videos = []
        durations = []

        # setting up the first video details
        first_video_path = videoPaths[0]
        first_video = Video()
        cap = cv2.VideoCapture(first_video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(frame_count / fps)
        videoName = os.path.basename(first_video_path)
        durationObj = datetime.timedelta(seconds=duration)
        first_video.path = first_video_path
        first_video.name = videoName
        first_video.duration = str(durationObj)

        for videoPath in videoPaths:
            video = Video()
            cap = cv2.VideoCapture(videoPath)
            fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = int(frame_count / fps)
            durations.append(duration)
            videoName = os.path.basename(videoPath)
            durationObj = datetime.timedelta(seconds=duration)
            video.path = videoPath
            video.name = videoName
            video.duration = str(durationObj)
            videos.append(video)
        context = {'Videos': videos, 'firstVideo': first_video, 'durations': durations, 'lecturer_subjects': lecturer_subjects, 'subjects': subject_list,
                   'template_name': 'FirstApp/template.html'}

    except Exception as ex:
        return redirect('/500')

    return render(request, 'FirstApp/video_results.html', context)


# view for emotion page
@login_required(login_url='/login')
def emotion_view(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    except Exception as exc:
        return redirect('/500')

    return render(request, "FirstApp/emotion.html",
                  {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})


# signing In the user
def loggedInView(request):
    username = "not logged in"
    message = "Invalid Username or Password"
    MyLoginForm = LoginForm(request.POST)

    print('message: ', message)

    try:
        # if the details are valid, let the user log in
        if MyLoginForm.is_valid():
            email = MyLoginForm.cleaned_data.get('email')
            password = MyLoginForm.cleaned_data.get('password')

            user = User.objects.get(email=email)
            lecturer = Lecturer.objects.get(email=email)

            login(request, user)
            # setting up the session
            request.session['lecturer'] = lecturer.id

            return redirect('/')

        else:
            message = "Please provide correct credntials"
    except Exception as exc:
        print('exception: ', exc)

    return render(request, 'FirstApp/login.html', {'message': message})


# signing out the user
def logoutView(request):

    logout(request)

    return redirect('/login')


# 500 error page
def view500(request):
    return render(request, "FirstApp/500.html")


# tables page
def tables(request):
    return render(request, "FirstApp/tables.html")

@login_required(login_url='/login')
def activity(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    except Exception as exc:
        return redirect('/500')

    return render(request, "FirstApp/activity.html", {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})