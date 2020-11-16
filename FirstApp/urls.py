"""

- this file will handle the urlpatterns for the 'FirstApp' application

- the 'urlpatterns' variable will contain the list of url patterns exist for this application

- inside this 'list' variable, the 'path' variable will accept the url mappings to be redirected
to an HTML page (view)

- the 'url' will accept the url mappings to be redirected to a RESTful endpoint


"""

from django.urls import path, re_path, include
from django.conf.urls import url
from rest_framework import routers
from . import views
from . import api

router = routers.DefaultRouter()
# router.register(r'^createImage', views.ImageViewSet)

urlpatterns = [
    path('', views.hello),
    path('login', views.loginForm),
    path('logout', views.logoutView),
    path('404', views.view404),
    path('401', views.view401),
    path('500', views.view500),
    path('gaze', views.gaze),
    path('template', views.template),

    # emotion path
    path('emotion', views.emotion_view),
    # video results
    path('video_result', views.video_result),

    # this is used to process login
    path('process-login', views.loggedInView),

    # this is used to process admin login
    path('process-admin-login', views.processAdminLogin),

    # this is used for user-redirect processing
    path('process-user-redirect', views.processUserRedirect),

    # this is used for admin login page
    path('admin-login', views.adminLogin),


    # this is used for activity
    path('activity', views.activity),

    # test view (delete later)
    path('test', views.test),


    # user direct view
    path('user-direct', views.userDirect),


    # testing the lecture in the API
    url(r'^lectures', api.LectureViewSet.as_view()),

    # faculty API
    url(r'^faculties', api.FacultyViewSet.as_view()),

    # subjects API
    url(r'^subjects', api.SubjectViewSet.as_view()),

    # lecturer API
    url(r'^lecturers', api.LecturerViewSet.as_view()),

    # lecturer-subjects API
    url(r'^lecturer-subjects', api.LecturerSubjectViewSet.as_view()),

    # timetable API
    url(r'^timetable', api.FacultyTimetableViewSet.as_view()),

    ##### VIDEO Section #####

    # lecture video API
    url(r'^lecture-video', api.LectureVideoViewSet.as_view()),

    # lecture video API (to retrieve a lecture)
    url(r'^get-lecture-video/$', api.GetLectureVideoViewSet.as_view()),

    # lecture video API (to retrieve a lecture video in the lecturer home page)
    url(r'^get-lecture-video-for-home/$', api.GetLectureVideoViewSetForHome.as_view()),


    ##### ACTIVITIES API #####

    # lecture activity API (to retrieve lecture activities)
    url(r'^lecture-activities/', api.LectureActivityViewSet.as_view()),

    # lecture activity API (to retrieve a lecture activity)
    url(r'^get-lecture-activity/$', api.GetLectureActivityViewSet.as_view()),

    # lecture activity API (to retrieve a lecture activity)
    url(r'^process-lecture-activity/$', api.LectureActivityProcess.as_view()),

    # lecture activity detection for frames API (to retrieve detections for each frame in lecture video)
    url(r'^get-lecture-activity-for-frame/$', api.GetLectureActivityRecognitionsForFrames.as_view()),

    # lecture activity report generation
    url(r'^lecture-activity-report-generation/$',
        api.GenerateActivityReport.as_view()),


    ###### EMOTION Section #####
    # getting lecture emotion record availability
    url(r'^get-lecture-emotion-availability/$', api.GetLectureEmotionAvailability.as_view()),

    # getting lecture emotion record
    url(r'^get-lecture-emotion/$', api.GetLectureEmotionReportViewSet.as_view()),

    # process a lecture emotion record
    url(r'^process-lecture-emotion/$', api.LectureEmotionProcess.as_view()),

    # lecture emotion detection for frames API (to retrieve detections for each frame in lecture video)
    url(r'^get-lecture-emotion-for-frame/$', api.GetLectureEmotionRecognitionsForFrames.as_view()),



    ##### GAZE Section #####
    # lecture video Gaze estimation
    url(r'^get-lecture-video-gaze-estimation-availability/$', api.GetLectureGazeEstimationAvailaibility.as_view()),

    # process a lecture Gaze estimation
    url(r'^process-lecture-gaze-estimation/$', api.ProcessLectureGazeEstimation.as_view()),

    # retrieve a Lecture Gaze estimation
    url(r'^get-lecture-gaze-estimation/$', api.GetLectureGazeEstimationViewSet.as_view()),

    # lecture gaze estimation for frames API (to retrieve detections for each frame in lecture video)
    url(r'^get-lecture-gaze-estimation-for-frame/$', api.GetLectureGazeEstimationForFrames.as_view()),


    #####===== DATA VISUALIZATION =====#####

    ##### VIEW STUDENT BEHAVIOR SUMMARY SECTION #####

    # retrieves student behavior summary for specified time period
    url(r'^get-student-behavior-summary-for-period/$', api.GetStudentBehaviorSummaryForPeriod.as_view()),

    # retrieves lecture video summary time landmarks
    url(r'^get-lecture-video-summary-time-landmarks/$', api.GetLectureVideoSummaryTimeLandmarks.as_view()),

    # retrieves lecture activity summary
    url(r'^get-lecture-activity-summary/$', api.GetLectureActivitySummary.as_view()),

    # retrieves lecture activity summary
    url(r'^get-lecture-emotion-summary/$', api.GetLectureEmotionSummary.as_view()),

    # retrieves lecture activity summary
    url(r'^get-lecture-gaze-summary/$', api.GetLectureGazeSummary.as_view()),

    # retrieves lecture activity summary
    url(r'^get-activity-correlations/$', api.GetLectureActivityCorrelations.as_view()),

    # retrieves lecture activity summary
    url(r'^get-emotion-correlations/$', api.GetLectureEmotionCorrelations.as_view()),

    # retrieves lecture activity summary
    url(r'^get-gaze-correlations/$', api.GetLectureGazeCorrelations.as_view()),


    ##### OTHERS #####

    # retrieves lecture recorded video name
    url(r'^get-lecture-recorded-video-name/$', api.GetLecturerRecordedVideo.as_view()),


    ##### BATCH PROCESS #####
    # perform batch process for student behavior
    url(r'^student-behavior-batch-process/$', api.BatchProcess.as_view()),

    # check availability for student behavior components
    url(r'^check-availability/$', api.CheckStudentBehaviorAvailability.as_view()),

    # perform random task (delete later)
    url(r'^get-random_number/$', api.TestRandom.as_view()),




    # routers
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
from rest_framework.urlpatterns import format_suffix_patterns
