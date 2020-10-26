from django.urls import path, re_path, include
from django.conf.urls import url
from rest_framework import routers
from . import views
from . import api

router = routers.DefaultRouter()
router.register(r'^register', views.RegisterViewSet)
# router.register(r'^createImage', views.ImageViewSet)

urlpatterns = [
    path('', views.hello),
    path('login', views.loginForm),
    path('logout', views.logoutView),
    path('register-user', views.register),
    path('404', views.view404),
    path('401', views.view401),
    path('500', views.view500),
    path('blank', views.blank),
    path('gaze', views.gaze),
    path('gaze-process', views.processGaze),
    path('pose', views.pose),
    path('charts', views.charts),
    path('forgot-password', views.forget_password),
    path('webcam', views.webcam),
    path('template', views.template),
    path('base', views.base),
    path('child', views.child),
    # extractor path
    path('extract', views.extractor),
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

    # tables view
    path('tables', views.tables),

    # test view (delete later)
    path('test', views.test),


    # user direct view
    path('user-direct', views.userDirect),

    url(r'^register', views.RegisterViewSet),
    # re_path('video/?video_name<str:video_name>', views.video),
    url(r'^teachers/', views.teachersList.as_view()),
    url(r'^video/', views.video, name='video'),

    url(r'^createImage', api.ImageViewSet.as_view()),
    # for gaze estimation
    url(r'^estimateGaze', api.GazeEstimationViewSet.as_view()),
    # for video extraction (POST)
    url(r'^videoExtract', api.VideoExtractionViewSet.as_view()),
    # for video extraction (GET)
    url(r'^videoExtract/(?P<folder_name>\D+)', api.VideoExtractionViewSet.as_view()),

    # testing the lecture emotions in the API
    url(r'^lecture_emotions', api.LectureEmotionViewSet.as_view()),

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

    # lecture video API (to retrieve a lecture)
    url(r'^get-lecture-video-for-home/$', api.GetLectureVideoViewSetForHome.as_view()),

    ##### ACTIVITIES API #####

    # lecture activity API (to retrieve lecture activities)
    url(r'^lecture-activities/', api.LectureActivityViewSet.as_view()),

    # lecture activity API (to retrieve a lecture activity)
    url(r'^get-lecture-activity/$', api.GetLectureActivityViewSet.as_view()),

    # lecture activity API (to retrieve a lecture activity)
    url(r'^process-lecture-activity/$', api.LectureActivityProcess.as_view()),

    # lecture activity detection API (to retrieve detections for a given lecture activity frame)
    url(r'^get-lecture-activity-frame-detection/$', api.GetLectureActivityDetections.as_view()),

    # lecture activity detection for label API (to retrieve detections for a certain label)
    url(r'^get-lecture-activity-detection-for-label/$', api.GetLectureActvityDetectionsForLabel.as_view()),

    # lecture activity detection for label API (to retrieve detections for a certain label)
    url(r'^get-lecture-activity-student-evaluation/$', api.GetLectureActivityStudentEvaluation.as_view()),

    # lecture activity detection for frames API (to retrieve detections for each frame in lecture video)
    url(r'^get-lecture-activity-for-frame/$', api.GetLectureActivityRecognitionsForFrames.as_view()),

    # lecture activity evaluation for individual students
    url(r'^get-lecture-activity-individual-student-evaluation/$',
        api.GetLectureActivityIndividualStudentEvaluation.as_view()),

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

    # lecture emotion evaluation for students
    url(r'^get-lecture-emotion-student-evaluation/$', api.GetLectureEmotionStudentEvaluations.as_view()),

    # lecture emotion evaluation for students
    url(r'^get-lecture-emotion-individual-student-evaluation/$',
        api.GetLectureEmotionIndividualStudentEvaluation.as_view()),

    # lecture emotion detection for frames API (to retrieve detections for each frame in lecture video)
    url(r'^get-lecture-emotion-for-frame/$', api.GetLectureEmotionRecognitionsForFrames.as_view()),


    ###### POSE Section #####
    # lecture video API (for Pose estimation)
    url(r'^get-lecture-video-for-pose/$', api.GetLectureVideoForPose.as_view()),

    # lecture video extracted frames API (for Pose estimation)
    url(r'^get-lecture-video-extracted-frames/$', api.GetLectureVideoExtractedFrames.as_view()),

    # lecture video individual student extracted frames API (for Pose estimation)
    url(r'^get-lecture-video-individual-student-frames/$', api.GetLectureVideoIndividualStudentFrames.as_view()),

    # lecture video individual student process pose estimation API (for Pose estimation)
    url(r'^process-lecture-video-individual-pose-estimation', api.ProcessIndividualStudentPoseEstimation.as_view()),


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


    # routers
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
from rest_framework.urlpatterns import format_suffix_patterns
