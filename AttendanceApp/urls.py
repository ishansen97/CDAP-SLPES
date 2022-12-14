from django.urls import path
from .api import student_list, student_detail, subject_list, subject_detail, attendance_list, StudentAPIView, \
    StudentDetails
from django.conf.urls import url
from .api import *
from . import views

urlpatterns = [
    path('students/', student_list),
    path('students/<str:pk>', student_detail),
    path('subjects/', subject_list),
    path('subjects/<str:pk>', subject_detail),
    path('attendance/', attendance_list),
    path('student/', StudentAPIView.as_view()),
    path('initiate-lecture', views.initiate_lecture),
    # class based
    path('student/', StudentAPIView.as_view()),
    path('student/<str:pk>', StudentDetails.as_view()),
    url(r'^upload/$', FileView.as_view(), name='file-upload'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    # this url will initiate the lecture
    url(r'^process-initiate-lecture/$', InitiateLecture.as_view()),

    # this url will be used for testing
    url(r'^test-api', TestAPI.as_view()),
    url(r'^stop-api/$', stopRecording.as_view()),
    url(r'^training-api/$', getTrainingImages.as_view()),

    # this url will be used for testing
    url(r'^lecture-video-api', LecturerVideoAPI.as_view()),
    url(r'^stop-lecture-api/$', stopRecording.as_view())

]
