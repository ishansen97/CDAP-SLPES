from django.urls import path, re_path, include
from . import views
from rest_framework import routers
from django.conf.urls import url
from . import api

router = routers.DefaultRouter()

urlpatterns = [
    path('lecture', views.summarization),
    # path('record', views.lectureRecord),


    # API to retrieve lecture summarizing details
    url(r'^lecture-audio', api.LectureAudioAPI.as_view()),

    url(r'^lecture-audio-noise-removed/$', api.AudioNoiseRemovedList.as_view()),

    url(r'^lecture-audio-to-text/$', api.AudioToTextList.as_view()),

    url(r'^lecture-summary/$', api.LectureSummaryList.as_view()),

    url(r'^lecture-notices/$', api.LectureNoticeList.as_view()),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]
