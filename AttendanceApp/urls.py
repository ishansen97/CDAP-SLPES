from django.urls import path
from .api import student_list, student_detail, subject_list, subject_detail, attendance_list, StudentAPIView, \
    StudentDetails
from django.conf.urls import url
from .api import FileView, InitiateLecture
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
    url(r'^process-initiate-lecture/$', InitiateLecture.as_view())
]
