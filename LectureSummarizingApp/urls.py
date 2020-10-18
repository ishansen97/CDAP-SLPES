from django.urls import path, re_path, include
from . import views
from rest_framework import routers
from django.conf.urls import url
from . import api

router = routers.DefaultRouter()
# router.register(r'^register', views.register)

urlpatterns = [
    # path('', views.hello),
    # path('login', views.login),
    # path('register', views.register),
    # path('404', views.view404),
    # path('blank', views.blank),
    # path('buttons', views.buttons),
    # path('cards', views.cards),
    # path('charts', views.charts),
    # path('forgot-password', views.forget_password),
    # # path('webcam', views.webcam),
    # path('template', views.template),
    # path('base', views.base),
    # path('child', views.child),
    # path('lecture-video', views.lecVideo),
    # # path('Video', views.hello)

    # API to retrieve activity recognition
    url(r'^get-lecture-audio/$', api.LectureAudioAPI.as_view()),

    # # API to retrieve audio analysis
    # url(r'^get-audio-analysis', api.GetLectureAudioAnalysis.as_view()),
    #
    # # API to retrieve lecture audio text
    # url(r'^get-lecture-audio-text', api.LectureAudioTextAPI.as_view()),
    #
    # # test API
    # url(r'^test-api', api.TestAPI.as_view()),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]
