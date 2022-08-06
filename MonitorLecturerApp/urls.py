from django.urls import path, re_path, include
from . import views
from rest_framework import routers
from django.conf.urls import url
from . import api

router = routers.DefaultRouter()
# router.register(r'^register', views.register)

urlpatterns = [
    path('', views.hello),
    path('lecture-video', views.lecVideo),
    # path('Video', views.hello)

    ##### LECTURER VIDEO SECTION #####
    # API to retrieve/save lecturer video details
    url(r'^lecturer-video/$', api.LecturerVideoAPI.as_view()),

    ##### LECTURER ACTIVITY SECTION #####
    # API to retrieve activity recognition
    url(r'^activities/$', api.ActivityRecognitionAPI.as_view()),

    # API to retrieve lecturer video meta data results
    url(r'^get-lecturer-video-results/$', api.GetLectureVideoResultsAPI.as_view()),

    # API to retrieve lecturer video frame recognitions
    url(r'^get-lecturer-video-frame-recognitions/$', api.StudentLecturerIntegratedAPI.as_view()),

    # API to process lecturer video frame recognitions
    url(r'^process-lecturer-video-frame-recognitions/$', api.ProcessLecturerFrameRecognitionsAPI.as_view()),

    ##### END OF LECTURER ACTIVITY SECTION #####


    ##### LECTURE AUDIO SECTION #####

    # API to retrieve audio analysis
    url(r'^get-audio-analysis/$', api.GetLectureAudioAnalysis.as_view()),

    # API to save audio analysis
    url(r'^process-lecture-audio-analysis/$', api.ProcessLectureAudioAnalysis.as_view()),

    # API to retrieve lecture audio text
    url(r'^get-lecture-audio-text', api.LectureAudioTextAPI.as_view()),

    # API to retrieve lecture audio text
    url(r'^get-lecturer-audio-summary-for-period', api.LecturerAudioSummaryPeriodAPI.as_view()),

    ##### END OF LECTURE AUDIO SECTION #####


    # test API
    url(r'^test-api', api.TestAPI.as_view()),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]
