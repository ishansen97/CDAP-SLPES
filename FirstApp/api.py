"""
this file is responsible for creating the API classes so that
frontend could communicate with the backend, through JSON-based communication

each class is extended by djangorestframework APIVIEW class

each class contains methods to represent the HTTP methods received through the requests
in this case the GET method was mostly used.

each method will return an HttpResponse that allows its data to be rendered into
arbitrary media types.

"""
import json
from random import Random

from apscheduler.jobstores.mongodb import MongoDBJobStore

from MonitorLecturerApp.models import LectureRecordedVideo, LecturerVideoMetaData
from MonitorLecturerApp.serializers import LectureRecordedVideoSerializer, LecturerVideoMetaDataSerializer
from rest_framework.views import *

from integrated_slpes.wsgi import application
from .logic import activity_recognition as ar
from . import emotion_detector as ed, automation_process as ap
from .logic import id_generator as ig
from .logic import pdf_file_generator as pdf
from .logic import head_gaze_estimation as hge
from .logic import video_extraction as ve
from . logic import student_behavior_process as sbp
from .logic.scheduler_tasks import task_scheduler
from .serializers import *
from braces.views import CsrfExemptMixin

from django.core.handlers.wsgi import WSGIRequest
from django.http.request import HttpRequest

import datetime
import os


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


# API for Faculties
class FacultyViewSet(APIView):

    def get(self, request):
        faculties = Faculty.objects.all().order_by('faculty_id')
        serializer = FacultySerializer(faculties, many=True)
        return Response(serializer.data)

    def post(self, request):
        Faculty(
            faculty_id=request.data['faculty_id'],
            name=request.data['name']
        ).save()
        return Response(status=201, data={"response": "successfully added"})


# API for subjects
class SubjectViewSet(APIView):

    def get(self, request):
        subjects = Subject.objects.all().order_by('subject_code')
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


# API for lecturers
class LecturerViewSet(APIView):

    def get(self, request):
        lecturers = Lecturer.objects.all().order_by('lecturer_id')
        serializer = LecturerSerializer(lecturers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LecturerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


# API for lecturers and their subjects
class LecturerSubjectViewSet(APIView):

    def get(self, request):
        lecturer_subjects = LecturerSubject.objects.all().order_by('lec_subject_id')
        serializer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LecturerSubjectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


# API for timetables
class FacultyTimetableViewSet(APIView):

    def get(self, request):
        timetable = FacultyTimetable.objects.all().filter()
        serializer = FacultyTimetableSerializer(timetable, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FacultyTimetableSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


# API for lecture videos
class LectureVideoViewSet(APIView):

    def get(self, request):
        lecture_videos = LectureVideo.objects.all()
        serializer = LectureVideoSerializer(lecture_videos, many=True)
        return Response(serializer.data)

    def post(self, request):

        # get the request data
        # data = request.data
        #
        # # retrieve the last lecture video details
        # last_lec_video = LectureVideo.objects.order_by('lecture_video_id').last()
        # # create the next lecture video id
        # new_lecture_video_id = ig.generate_new_id(last_lec_video.lecture_video_id)
        #
        # # create the new lecture video
        # LectureVideo(
        #     lecture_video_id=new_lecture_video_id,
        #     lecturer_id=data['lecturer_id'],
        #     subject_id=data['subject_id'],
        #     video_name=data['video_name'],
        #     video_length=data['video_length'],
        #     date=data['date']
        # ).save()
        #
        # # return the successful response
        # return Response({
        #     "response": "Successfully created",
        #
        # }, status=status.HTTP_201_CREATED)

        # serializer = LectureVideoSerializer(data=request.data, many=True)
        serializer = LectureVideoSerializer(data=request.data)
        # serializer.create(validated_data=request.data)
        data = {}
        data_ser = {}


        if serializer.is_valid(raise_exception=ValueError):
            data = serializer.create(validated_data=request.data)
            print('data: ', data)
            # data_ser = LectureVideoSerializer(data, many=True)

        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(data, status=status.HTTP_201_CREATED)


        # return Response(serializer.error_messages,
        #                 status=status.HTTP_400_BAD_REQUEST)


# this API will retrieve a lecture video details
class GetLectureVideoViewSet(APIView):

    def get(self, request):
        # get the lecturer id from the request
        lecturer = request.query_params.get('lecturer')
        # get the lecture date from the request
        date = request.query_params.get('date')
        # get the item number from the request
        index = int(request.query_params.get('index'))

        # retrieve the lecture video from the db
        lecturer_video = LectureVideo.objects.filter(lecturer_id=lecturer, date=date)
        # serialize the object
        serializer = LectureVideoSerializer(lecturer_video, many=True)

        # get the lecture video id
        lecture_video_id = serializer.data[0]['lecture_video_id']
        print('lecture video id: ', lecture_video_id)

        # retrieve the lecture activties exist for the given video
        activities = LectureActivity.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)

        # assign the whether there are found lecture activites or not
        isActivityFound = (len(activities) > 0)

        # return the response
        return Response({
            "response": serializer.data[index],
            "isActivityFound": isActivityFound
        })


# this API will retrieve lecture video details for lecturer Home Page
class GetLectureVideoViewSetForHome(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        date = request.query_params.get('date')
        counter = int(request.query_params.get('counter'))
        lecturer_video = LectureVideo.objects.filter(lecturer_id=lecturer, date=date)
        serializer = LectureVideoSerializer(lecturer_video, many=True)

        response = {}

        # to check whether there is only one lecture video for the query

        # if there are more than one, send only the specified lecture video
        if len(serializer.data) > 1:
            response = serializer.data[counter]
        # else, send the only lecture video
        else:
            response = serializer.data[0]

        # return the response
        return Response({
            "response": response
        })



##### ACTIVITY section #####

# API for lecture activities
class LectureActivityViewSet(APIView):

    def get(self, request):
        lecture_activities = LectureActivity.objects.all()
        serializer = LectureActivitySerializer(lecture_activities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LectureActivitySerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


# API to retrieve one lecture activity
class GetLectureActivityViewSet(APIView):

    def get(self, request):
        lecture_video_id = request.query_params.get('lecture_video_id')
        lecture_activities = LectureActivity.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        serializer = LectureActivitySerializer(lecture_activities, many=True)

        return Response({
            "response": serializer.data,
        })


# API to process lecture activity and save to DB
class LectureActivityProcess(APIView):

    def get(self, request):
        video_name = request.query_params.get('lecture_video_name')
        video_id = int(request.query_params.get('lecture_video_id'))
        percentages = ar.activity_recognition(video_name)
        self.activity(video_id, percentages)
        return Response({"response": True})


    def activity(self, lec_video_id, percentages):
        # lec_video = LectureVideo.objects.filter(lecture_video_id=lec_video_id)
        lec_video = LectureVideo.objects.filter(id=lec_video_id)
        lec_video_serializer = LectureVideoSerializer(lec_video, many=True)
        lec_video_data = lec_video_serializer.data[0]

        last_lec_activity = LectureActivity.objects.order_by('lecture_activity_id').last()
        new_lecture_activity_id = ig.generate_new_id(last_lec_activity.lecture_activity_id)

        # creating a new lecture activity
        LectureActivity(
            lecture_activity_id=new_lecture_activity_id,
            lecture_video_id_id=lec_video_id,
            phone_perct=percentages['phone_perct'],
            listening_perct=percentages['listening_perct'],
            writing_perct=percentages['writing_perct']
        ).save()

        # get the video name
        video_name = lec_video_data['video_name']

        # then save the frame recognitions to the database
        _ = ar.save_frame_recognition(video_name)

        # save the time landmarks and frame landmarks
        ve.save_time_landmarks(video_name)
        frame_landmarks, frame_group_dict = ve.save_frame_landmarks(video_name)

        # then save the activity frame groupings
        ar.save_frame_groupings(video_name, frame_landmarks, frame_group_dict)


# API to retrieve activity detections for frames
class GetLectureActivityRecognitionsForFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # finding the existence of Lecture activity frame recognition record
        isExist = LectureActivityFrameRecognitions.objects.filter(lecture_activity_id__lecture_video_id__video_name=video_name).exists()

        if (isExist):
            lecture_activity_frame_recognitions = LectureActivityFrameRecognitions.objects.filter(lecture_activity_id__lecture_video_id__video_name=video_name)
            lecture_activity_frame_recognitions_ser = LectureActivityFrameRecognitionsSerializer(lecture_activity_frame_recognitions, many=True)
            lecture_activity_frame_recognitions_data = lecture_activity_frame_recognitions_ser.data[0]

            frame_detections = lecture_activity_frame_recognitions_data['frame_recognition_details']

            return Response({
                "response": frame_detections
            })

        else:

            # perform the action of saving frame recognitions to database
            frame_detections = ar.save_frame_recognition(video_name)

            return Response({
                "response": frame_detections
            })


# API to create reports for Activity
class GenerateActivityReport(APIView):

    def get(self, request):
        subject = request.query_params.get('subject')
        lecturer = int(request.query_params.get('lecturer'))
        date = request.query_params.get('date')

        # retrieve the subject name
        subject_query = Subject.objects.filter(subject_code=subject)
        subject_serializer = SubjectSerializer(subject_query, many=True)
        subject_name = subject_serializer.data[0]['name']

        # retrieve the lecturer name
        # lecturer_query = Lecturer.objects.filter(lecturer_id=lecturer)
        lecturer_query = Lecturer.objects.filter(id=lecturer)
        lecturer_serializer = LecturerSerializer(lecturer_query, many=True)
        lecturer_lname = lecturer_serializer.data[0]['lname']
        lecturer_fname = lecturer_serializer.data[0]['fname']
        lecturer_fullname = lecturer_fname + " " + lecturer_lname

        # set the dictionary
        object = {}
        object['subject_name'] = subject_name
        object['lecturer_name'] = lecturer_fullname
        object['date'] = date

        pdf.generate_pdf_file(object)

        return Response({
            "response": "success"
        })


###### EMOTIONS section #####
class GetLectureEmotionAvailability(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        date = request.query_params.get('date')
        index = int(request.query_params.get('index'))
        lecturer_emotion = LectureVideo.objects.filter(lecturer_id=lecturer, date=date)
        serializer = LectureVideoSerializer(lecturer_emotion, many=True)

        lecture_video_id = serializer.data[index]['lecture_video_id']
        activities = LectureEmotionReport.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        isActivityFound = (len(activities) > 0)

        return Response({
            "response": serializer.data[index],
            "isActivityFound": isActivityFound
        })


# to process lecture emotions for a lecture video
class LectureEmotionProcess(APIView):

    def get(self, request):
        video_name = request.query_params.get('lecture_video_name')
        # video_id = request.query_params.get('lecture_video_id')
        int_video_id = int(request.query_params.get('lecture_video_id'))
        percentages = ed.detect_emotion(video_name)
        percentages.calcPercentages()
        self.save_emotion_report(int_video_id, percentages)
        return Response({"response": True})

    def post(self, request):
        pass

    def save_emotion_report(self, lec_video_id, percentages):
        # lec_video = LectureVideo.objects.filter(lecture_video_id=lec_video_id)
        lec_video = LectureVideo.objects.filter(id=lec_video_id)
        lec_video_serializer = LectureVideoSerializer(lec_video, many=True)
        lec_video_data = lec_video_serializer.data[0]
        last_lec_emotion = LectureEmotionReport.objects.order_by('lecture_emotion_id').last()
        new_lecture_emotion_id = ig.generate_new_id(last_lec_emotion.lecture_emotion_id)

        lecture_video_id = lec_video_data['id']

        # creating a new lecture emotion report
        LectureEmotionReport(
            lecture_emotion_id=new_lecture_emotion_id,
            lecture_video_id_id=lecture_video_id,
            happy_perct=percentages.happy_perct,
            sad_perct=percentages.sad_perct,
            angry_perct=percentages.angry_perct,
            neutral_perct=percentages.neutral_perct,
            surprise_perct=percentages.surprise_perct
        ).save()

        # get the video name
        video_name = lec_video_data['video_name']

        # then save the frame recognition details to the database
        _ = ed.save_frame_recognitions(video_name)

        # retrieve the frame landmarks and frame group dictionary
        frame_landmarks, frame_group_dict = ve.getFrameLandmarks(video_name, "Emotion")

        # then save emotion frame groupings
        ed.save_frame_groupings(video_name, frame_landmarks, frame_group_dict)




# to get a lecture emotion report
class GetLectureEmotionReportViewSet(APIView):

    def get(self, request):
        lecture_video_id = request.query_params.get('lecture_video_id')

        lecture_emotions = LectureEmotionReport.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        serializer = LectureEmotionSerializer(lecture_emotions, many=True)

        print('data: ', serializer.data)

        return Response({
            "response": serializer.data,
        })


# API to retrieve emotion detections for frames
class GetLectureEmotionRecognitionsForFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # finding the existence of Lecture emotion frame recognition record
        isExist = LectureEmotionFrameRecognitions.objects.filter(
            lecture_emotion_id__lecture_video_id__video_name=video_name).exists()

        if (isExist):
            lecture_emotion_frame_recognitions = LectureEmotionFrameRecognitions.objects.filter(
                lecture_emotion_id__lecture_video_id__video_name=video_name)
            lecture_emotion_frame_recognitions_ser = LectureEmotionFrameRecognitionsSerializer(
                lecture_emotion_frame_recognitions, many=True)
            lecture_emotion_frame_recognitions_data = lecture_emotion_frame_recognitions_ser.data[0]

            frame_detections = lecture_emotion_frame_recognitions_data['frame_recognition_details']

            return Response({
                "response": frame_detections
            })

        else:
            # save the frame recognitions into the database
            frame_detections = ed.save_frame_recognitions(video_name)

            return Response({
                "response": frame_detections
            })


##### GAZE ESTIMATION SECTION #####
class GetLectureGazeEstimationAvailaibility(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        date = request.query_params.get('date')
        index = int(request.query_params.get('index'))
        lecturer_video = LectureVideo.objects.filter(lecturer_id=lecturer, date=date)
        serializer = LectureVideoSerializer(lecturer_video, many=True)

        lecture_video_id = serializer.data[index]['lecture_video_id']
        gaze_estimation = LectureGazeEstimation.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        isGazeEstimationFound = (len(gaze_estimation) > 0)

        return Response({
            "response": serializer.data[index],
            "isGazeEstimationFound": isGazeEstimationFound
        })


# the API to process lecture gaze estimation
class ProcessLectureGazeEstimation(APIView):

    def get(self, request):
        video_name = request.query_params.get('lecture_video_name')
        video_id = request.query_params.get('lecture_video_id')
        percentages = hge.process_gaze_estimation(video_name)
        self.estimate_gaze(video_id, percentages)
        return Response({"response": True})

    def post(self, request):
        pass

    def estimate_gaze(self, lec_video_id, percentages):
        # lec_video = LectureVideo.objects.filter(lecture_video_id=lec_video_id)
        lec_video = LectureVideo.objects.filter(id=lec_video_id)
        last_lec_gaze = LectureGazeEstimation.objects.order_by('lecture_gaze_id').last()
        lec_video_serializer = LectureVideoSerializer(lec_video, many=True)
        lec_video_data = lec_video_serializer.data[0]
        new_lecture_gaze_id = "LG000001" if (last_lec_gaze is None) else ig.generate_new_id(
            last_lec_gaze.lecture_gaze_id)
        new_lecture_gaze_primary_id = 1 if (last_lec_gaze is None) else int(last_lec_gaze.id) + 1


        # get the video id
        lecture_video_id = lec_video_data['id']

        # creating a new lecture gaze estimation
        LectureGazeEstimation(
            id=new_lecture_gaze_primary_id,
            lecture_gaze_id=new_lecture_gaze_id,
            lecture_video_id_id=lecture_video_id,
            looking_up_and_right_perct=percentages['head_up_right_perct'],
            looking_up_and_left_perct=percentages['head_up_left_perct'],
            looking_down_and_right_perct=percentages['head_down_right_perct'],
            looking_down_and_left_perct=percentages['head_down_left_perct'],
            looking_front_perct=percentages['head_front_perct']
        ).save()

        # get the video name
        video_name = lec_video_data['video_name']

        # then save the frame recognitions to the database
        _ = hge.save_frame_detections(video_name)

        # get the frame landmarks and frame group dictionary
        frame_landmarks, frame_group_dict = ve.getFrameLandmarks(video_name, "Gaze")

        # then save the gaze frame groupings to the database
        hge.save_frame_groupings(video_name, frame_landmarks, frame_group_dict)


# the API to retrieve lecture gaze estimation
class GetLectureGazeEstimationViewSet(APIView):

    def get(self, request):
        lecture_video_id = request.query_params.get('lecture_video_id')
        lecture_gaze_estimations = LectureGazeEstimation.objects.filter(
            lecture_video_id__lecture_video_id=lecture_video_id)
        serializer = LectureGazeEstimationSerializer(lecture_gaze_estimations, many=True)

        return Response({
            "response": serializer.data,
        })


# the API to retrieve Gaze estimation for frames
class GetLectureGazeEstimationForFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # finding the existence of Lecture gaze frame recognition record
        isExist = LectureGazeFrameRecognitions.objects.filter(
            lecture_gaze_id__lecture_video_id__video_name=video_name).exists()

        if (isExist):
            lecture_gaze_frame_recognitions = LectureGazeFrameRecognitions.objects.filter(
                lecture_gaze_id__lecture_video_id__video_name=video_name)
            lecture_gaze_frame_recognitions_ser = LectureGazeFrameRecognitionsSerializer(
                lecture_gaze_frame_recognitions, many=True)
            lecture_gaze_frame_recognitions_data = lecture_gaze_frame_recognitions_ser.data[0]

            frame_detections = lecture_gaze_frame_recognitions_data['frame_recognition_details']

            return Response({
                "response": frame_detections
            })

        else:

            # save recognition details into the database
            frame_detections = hge.save_frame_detections(video_name)

            return Response({
                "response": frame_detections
            })



##### VIDEO RESULTS SECTION #####

# this API find the lectures which are yet to be processed
class LectureProcessAvailability(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        lecturer_videos = LectureVideo.objects.filter(lecturer_id=lecturer)
        serializer = LectureVideoSerializer(lecturer_videos, many=True)

        data = serializer.data

        for video in data:
            print('video name: ', video['video_name'])

        return Response({
            "response": "hello"
        })


##### VIEW STUDENT BEHAVIOR SUMMARY SECTION #####

# this API will retrieve student behavior summary for specified time period
class GetStudentBehaviorSummaryForPeriod(APIView):

    def get(self, request):
        option = request.query_params.get('option')
        lecturer = request.query_params.get('lecturer')
        int_lecturer = int(lecturer)
        int_option = int(option)
        # int_option = 150
        isRecordFound = False
        activity_percentages = {}
        emotion_percentages = {}
        gaze_estimation_percentages = {}

        individual_lec_activties = []
        individual_lec_emotions = []
        individual_lec_gaze_estimations = []

        activity_labels = []
        emotion_labels = []
        gaze_estimation_labels = []


        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        previous_date = current_date - option_date

        # retrieving lecture activities
        lec_activity = LectureActivity.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        if len(lec_activity) > 0:
            isRecordFound = True
            activity_serializer = LectureActivitySerializer(lec_activity, many=True)
            activity_data = activity_serializer.data
            activity_percentages, individual_lec_activties, activity_labels = ar.get_student_activity_summary_for_period(activity_data)

        # retrieving lecture emotions
        lec_emotion = LectureEmotionReport.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        if len(lec_emotion) > 0:
            emotion_serializer = LectureEmotionSerializer(lec_emotion, many=True)
            emotion_data = emotion_serializer.data
            emotion_percentages, individual_lec_emotions, emotion_labels = ed.get_student_emotion_summary_for_period(emotion_data)


        # retrieving lecture gaze estimations
        lec_gaze_estimation = LectureGazeEstimation.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        # if there are gaze estimation data
        if len(lec_gaze_estimation) > 0:
            gaze_estimation_serializer = LectureGazeEstimationSerializer(lec_gaze_estimation, many=True)
            gaze_estimation_data = gaze_estimation_serializer.data
            gaze_estimation_percentages, individual_lec_gaze_estimations, gaze_estimation_labels = hge.get_student_gaze_estimation_summary_for_period(gaze_estimation_data)


        return Response({
            "activity_response": activity_percentages,
            "emotion_response": emotion_percentages,
            "gaze_estimation_response": gaze_estimation_percentages,
            "individual_activities": individual_lec_activties,
            "individual_emotions": individual_lec_emotions,
            "individual_gaze_estimations": individual_lec_gaze_estimations,
            "activity_labels": activity_labels,
            "emotion_labels": emotion_labels,
            "gaze_estimation_labels": gaze_estimation_labels,
            "isRecordFound": isRecordFound
        })


# this API will retrieve lecture video summary time landmarks
class GetLectureVideoSummaryTimeLandmarks(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # checking for the existing time landmarks details
        isExist = LectureVideoTimeLandmarks.objects.filter(lecture_video_id__video_name=video_name).exists()

        if (isExist):
            time_landmarks = []
            lec_video_time_landmarks = LectureVideoTimeLandmarks.objects.filter(lecture_video_id__video_name=video_name)
            lec_video_time_landmarks_ser = LectureVideoTimeLandmarksSerializer(lec_video_time_landmarks, many=True)
            lec_video_time_landmarks_data = lec_video_time_landmarks_ser.data[0]

            retrieved_landmarks = lec_video_time_landmarks_data["time_landmarks"]

            for landmark in retrieved_landmarks:
                time_landmarks.append(landmark['landmark'])

            # return the response
            return Response({
                "response": time_landmarks
            })

        # else:
        #
        #
        #     last_lec_video_time_landmarks = LectureVideoTimeLandmarks.objects.order_by('lecture_video_time_landmarks_id').last()
        #     new_lecture_video_time_landmarks_id = "LVTL00001" if (last_lec_video_time_landmarks is None) else \
        #         ig.generate_new_id(last_lec_video_time_landmarks.lecture_video_time_landmarks_id)
        #
        #
        #     # retrieve lecture video details
        #     lec_video = LectureVideo.objects.filter(video_name=video_name)
        #     lec_video_ser = LectureVideoSerializer(lec_video, many=True)
        #     lec_video_id = lec_video_ser.data[0]['id']
        #
        #
        #     # save the landmark details in the db
        #     time_landmarks = ve.getTimeLandmarks(video_name)
        #
        #     db_time_landmarks = []
        #
        #     # loop through the time landmarks
        #     for landmark in time_landmarks:
        #         landmark_obj = Landmarks()
        #         landmark_obj.landmark = landmark
        #
        #         db_time_landmarks.append(landmark_obj)
        #
        #
        #     new_lec_video_time_landmarks = LectureVideoTimeLandmarks()
        #     new_lec_video_time_landmarks.lecture_video_time_landmarks_id = new_lecture_video_time_landmarks_id
        #     new_lec_video_time_landmarks.lecture_video_id_id = lec_video_id
        #     new_lec_video_time_landmarks.time_landmarks = db_time_landmarks
        #
        #     new_lec_video_time_landmarks.save()
        #
        #     return Response({
        #         "response": time_landmarks
        #     })


# this API will retrieve lecture activity summary
class GetLectureActivitySummary(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        phone_perct = request.query_params.get('phone_perct')
        listen_perct = request.query_params.get('listen_perct')
        note_perct = request.query_params.get('note_perct')

        # checking the existence of lecture activity frame grouping records in the db
        isExist = LectureActivityFrameGroupings.objects.filter(lecture_activity_id__lecture_video_id__video_name=video_name).exists()

        if (isExist):
            # frame_landmarks, frame_group_dict = ve.getFrameLandmarks(video_name)
            frame_group_percentages = {}
            frame_landmarks = []

            # retrieve frame landmarks from db
            lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.filter(lecture_video_id__video_name=video_name)
            lec_video_frame_landmarks_ser = LectureVideoFrameLandmarksSerializer(lec_video_frame_landmarks, many=True)
            lec_video_frame_landmarks_data = lec_video_frame_landmarks_ser.data[0]

            retrieved_frame_landmarks = lec_video_frame_landmarks_data["frame_landmarks"]

            for landmark in retrieved_frame_landmarks:
                frame_landmarks.append(landmark['landmark'])


            lec_activity_frame_groupings = LectureActivityFrameGroupings.objects.filter(lecture_activity_id__lecture_video_id__video_name=video_name)
            lec_activity_frame_groupings_ser = LectureActivityFrameGroupingsSerializer(lec_activity_frame_groupings, many=True)
            lec_activity_frame_groupings_data = lec_activity_frame_groupings_ser.data[0]

            frame_group_details = lec_activity_frame_groupings_data["frame_group_details"]


            # create the new dictionary
            for group in frame_group_details:
                frame_group_percentages[group['frame_group']] = group['frame_group_percentages']



            class_labels = ['phone_perct', 'listen_perct', 'note_perct']

            # get the comments list
            comments = sbp.generate_student_behavior_comments("Activity", phone_perct=phone_perct, listen_perct=listen_perct, note_perct=note_perct)

            return Response({
                "frame_landmarks": frame_landmarks,
                "frame_group_percentages": frame_group_percentages,
                "activity_labels": class_labels,
                "comments": comments
            })

        # else:
        #
        #     # retrieve the previous lecture video frame landmarks details
        #     last_lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.order_by(
        #         'lecture_video_frame_landmarks_id').last()
        #     new_lecture_video_frame_landmarks_id = "LVFL00001" if (last_lec_video_frame_landmarks is None) else \
        #         ig.generate_new_id(last_lec_video_frame_landmarks.lecture_video_frame_landmarks_id)
        #
        #
        #     frame_landmarks, frame_group_dict = ve.getFrameLandmarks(video_name, "Activity")
        #     frame_group_percentages, activity_labels = ar.activity_frame_groupings(video_name, frame_landmarks, frame_group_dict)
        #
        #
        #     # retrieve lecture video details
        #     lec_video = LectureVideo.objects.filter(video_name=video_name)
        #     lec_video_ser = LectureVideoSerializer(lec_video, many=True)
        #     lec_video_id = lec_video_ser.data[0]['id']
        #
        #
        #     # save the frame landmarks details into db (temp method)
        #     db_frame_landmarks = []
        #
        #     for landmark in frame_landmarks:
        #         landmark_obj = Landmarks()
        #         landmark_obj.landmark = landmark
        #
        #         db_frame_landmarks.append(landmark_obj)
        #
        #
        #     new_lec_video_frame_landmarks = LectureVideoFrameLandmarks()
        #     new_lec_video_frame_landmarks.lecture_video_frame_landmarks_id = new_lecture_video_frame_landmarks_id
        #     new_lec_video_frame_landmarks.lecture_video_id_id = lec_video_id
        #     new_lec_video_frame_landmarks.frame_landmarks = db_frame_landmarks
        #
        #     new_lec_video_frame_landmarks.save()
        #
        #
        #
        #     # save the frame group details into db (temp method)
        #
        #     last_lec_activity_frame_grouping = LectureActivityFrameGroupings.objects.order_by('lecture_activity_frame_groupings_id').last()
        #     new_lecture_activity_frame_grouping_id = "LAFG00001" if (last_lec_activity_frame_grouping is None) else \
        #         ig.generate_new_id(last_lec_activity_frame_grouping.lecture_activity_frame_groupings_id)
        #
        #     # retrieve the lecture activity id
        #     lec_activity = LectureActivity.objects.filter(lecture_video_id__video_name=video_name)
        #     lec_activity_ser = LectureActivitySerializer(lec_activity, many=True)
        #     lec_activity_id = lec_activity_ser.data[0]['id']
        #
        #     # create the frame group details
        #     frame_group_details = []
        #
        #     for key in frame_group_percentages.keys():
        #         # create an object of type 'LectureActivityFrameGroupDetails'
        #         lec_activity_frame_group_details = LectureActivityFrameGroupDetails()
        #         lec_activity_frame_group_details.frame_group = key
        #         lec_activity_frame_group_details.frame_group_percentages = frame_group_percentages[key]
        #
        #         frame_group_details.append(lec_activity_frame_group_details)
        #
        #
        #     new_lec_activity_frame_groupings = LectureActivityFrameGroupings()
        #     new_lec_activity_frame_groupings.lecture_activity_frame_groupings_id = new_lecture_activity_frame_grouping_id
        #     new_lec_activity_frame_groupings.lecture_activity_id_id = lec_activity_id
        #     new_lec_activity_frame_groupings.frame_group_details = frame_group_details
        #
        #     # save
        #     new_lec_activity_frame_groupings.save()
        #
        #
        #     return Response({
        #         "frame_landmarks": frame_landmarks,
        #         "frame_group_percentages": frame_group_percentages,
        #         "activity_labels": activity_labels
        #     })


# this API will retrieve lecture emotion summary
class GetLectureEmotionSummary(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # checking the existence of lecture activity frame grouping records in the db
        isExist = LectureEmotionFrameGroupings.objects.filter(lecture_emotion_id__lecture_video_id__video_name=video_name).exists()

        if (isExist):
            frame_group_percentages = {}
            frame_landmarks = []

            # retrieve frame landmarks from db
            lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.filter(lecture_video_id__video_name=video_name)
            lec_video_frame_landmarks_ser = LectureVideoFrameLandmarksSerializer(lec_video_frame_landmarks, many=True)
            lec_video_frame_landmarks_data = lec_video_frame_landmarks_ser.data[0]

            retrieved_frame_landmarks = lec_video_frame_landmarks_data["frame_landmarks"]

            # creating a new list to display in the frontend
            for landmark in retrieved_frame_landmarks:
                frame_landmarks.append(landmark['landmark'])

            # retrieve emotion frame groupings details
            lec_emotion_frame_groupings = LectureEmotionFrameGroupings.objects.filter(lecture_emotion_id__lecture_video_id__video_name=video_name)
            lec_emotion_frame_groupings_ser = LectureEmotionFrameGroupingsSerializer(lec_emotion_frame_groupings, many=True)
            lec_emotion_frame_groupings_data = lec_emotion_frame_groupings_ser.data[0]

            frame_group_details = lec_emotion_frame_groupings_data["frame_group_details"]


            # create the new dictionary
            for group in frame_group_details:
                frame_group_percentages[group['frame_group']] = group['frame_group_percentages']


            class_labels = ['happy_perct', 'sad_perct', 'angry_perct', 'surprise_perct', 'neutral_perct']

            return Response({
                "frame_landmarks": frame_landmarks,
                "frame_group_percentages": frame_group_percentages,
                "emotion_labels": class_labels
            })

        else:

            frame_landmarks = []

            # retrieve frame landmarks from db
            lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.filter(
                lecture_video_id__video_name=video_name)
            lec_video_frame_landmarks_ser = LectureVideoFrameLandmarksSerializer(lec_video_frame_landmarks, many=True)
            lec_video_frame_landmarks_data = lec_video_frame_landmarks_ser.data[0]

            retrieved_frame_landmarks = lec_video_frame_landmarks_data["frame_landmarks"]

            # creating a new list to display in the frontend
            for landmark in retrieved_frame_landmarks:
                frame_landmarks.append(int(landmark['landmark']))


            l, frame_group_dict = ve.getFrameLandmarks(video_name, "Emotion")
            frame_group_percentages, emotion_labels = ed.emotion_frame_groupings(video_name, frame_landmarks, frame_group_dict)



            # save the frame group details into db (temp method)

            last_lec_emotion_frame_grouping = LectureEmotionFrameGroupings.objects.order_by('lecture_emotion_frame_groupings_id').last()
            new_lecture_emotion_frame_grouping_id = "LEFG00001" if (last_lec_emotion_frame_grouping is None) else \
                ig.generate_new_id(last_lec_emotion_frame_grouping.lecture_emotion_frame_groupings_id)

            # retrieve the lecture emotion id
            lec_emotion = LectureEmotionReport.objects.filter(lecture_video_id__video_name=video_name)
            lec_emotion_ser = LectureEmotionSerializer(lec_emotion, many=True)
            lec_emotion_id = lec_emotion_ser.data[0]['id']

            # create the frame group details
            frame_group_details = []

            for key in frame_group_percentages.keys():
                # create an object of type 'LectureActivityFrameGroupDetails'
                lec_emotion_frame_group_details = LectureEmotionFrameGroupDetails()
                lec_emotion_frame_group_details.frame_group = key
                lec_emotion_frame_group_details.frame_group_percentages = frame_group_percentages[key]

                frame_group_details.append(lec_emotion_frame_group_details)


            new_lec_emotion_frame_groupings = LectureEmotionFrameGroupings()
            new_lec_emotion_frame_groupings.lecture_emotion_frame_groupings_id = new_lecture_emotion_frame_grouping_id
            new_lec_emotion_frame_groupings.lecture_emotion_id_id = lec_emotion_id
            new_lec_emotion_frame_groupings.frame_group_details = frame_group_details

            # save
            new_lec_emotion_frame_groupings.save()


            return Response({
                "frame_landmarks": frame_landmarks,
                "frame_group_percentages": frame_group_percentages,
                "emotion_labels": emotion_labels
            })


# this API will retrieve lecture gaze summary
class GetLectureGazeSummary(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # checking the existence of lecture activity frame grouping records in the db
        isExist = LectureGazeFrameGroupings.objects.filter(lecture_gaze_id__lecture_video_id__video_name=video_name).exists()

        if (isExist):
            # frame_landmarks, frame_group_dict = ve.getFrameLandmarks(video_name)
            frame_group_percentages = {}
            frame_landmarks = []

            # retrieve frame landmarks from db
            lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.filter(lecture_video_id__video_name=video_name)
            lec_video_frame_landmarks_ser = LectureVideoFrameLandmarksSerializer(lec_video_frame_landmarks, many=True)
            lec_video_frame_landmarks_data = lec_video_frame_landmarks_ser.data[0]

            retrieved_frame_landmarks = lec_video_frame_landmarks_data["frame_landmarks"]

            for landmark in retrieved_frame_landmarks:
                frame_landmarks.append(landmark['landmark'])

            # retrieve the frame groupings
            lec_gaze_frame_groupings = LectureGazeFrameGroupings.objects.filter(lecture_gaze_id__lecture_video_id__video_name=video_name)
            lec_gaze_frame_groupings_ser = LectureGazeFrameGroupingsSerializer(lec_gaze_frame_groupings, many=True)
            lec_gaze_frame_groupings_data = lec_gaze_frame_groupings_ser.data[0]

            # take the frame group details out of it
            frame_group_details = lec_gaze_frame_groupings_data["frame_group_details"]


            # create the new dictionary
            for group in frame_group_details:
                frame_group_percentages[group['frame_group']] = group['frame_group_percentages']


            class_labels = ['upright_perct', 'upleft_perct', 'downright_perct', 'downleft_perct', 'front_perct']

            return Response({
                "frame_landmarks": frame_landmarks,
                "frame_group_percentages": frame_group_percentages,
                "gaze_labels": class_labels
            })

        else:

            frame_landmarks = []

            # retrieve frame landmarks from db
            lec_video_frame_landmarks = LectureVideoFrameLandmarks.objects.filter(
                lecture_video_id__video_name=video_name)
            lec_video_frame_landmarks_ser = LectureVideoFrameLandmarksSerializer(lec_video_frame_landmarks, many=True)
            lec_video_frame_landmarks_data = lec_video_frame_landmarks_ser.data[0]

            retrieved_frame_landmarks = lec_video_frame_landmarks_data["frame_landmarks"]

            # creating a new list to display in the frontend
            for landmark in retrieved_frame_landmarks:
                frame_landmarks.append(int(landmark['landmark']))


            l, frame_group_dict = ve.getFrameLandmarks(video_name, "Gaze")
            print('frame group dict: ', frame_group_dict)
            frame_group_percentages, gaze_labels = hge.gaze_estimation_frame_groupings(video_name, frame_landmarks, frame_group_dict)

            # save the frame group details into db (temp method)

            last_lec_gaze_frame_grouping = LectureGazeFrameGroupings.objects.order_by('lecture_gaze_frame_groupings_id').last()
            new_lecture_gaze_frame_grouping_id = "LGFG00001" if (last_lec_gaze_frame_grouping is None) else \
                ig.generate_new_id(last_lec_gaze_frame_grouping.lecture_gaze_frame_groupings_id)

            # retrieve the lecture activity id
            lec_gaze = LectureGazeEstimation.objects.filter(lecture_video_id__video_name=video_name)
            lec_gaze_ser = LectureGazeEstimationSerializer(lec_gaze, many=True)
            lec_gaze_id = lec_gaze_ser.data[0]['id']

            # create the frame group details
            frame_group_details = []

            for key in frame_group_percentages.keys():
                # create an object of type 'LectureActivityFrameGroupDetails'
                lec_gaze_frame_group_details = LectureGazeFrameGroupDetails()
                lec_gaze_frame_group_details.frame_group = key
                lec_gaze_frame_group_details.frame_group_percentages = frame_group_percentages[key]

                frame_group_details.append(lec_gaze_frame_group_details)


            new_lec_gaze_frame_groupings = LectureGazeFrameGroupings()
            new_lec_gaze_frame_groupings.lecture_gaze_frame_groupings_id = new_lecture_gaze_frame_grouping_id
            new_lec_gaze_frame_groupings.lecture_gaze_id_id = lec_gaze_id
            new_lec_gaze_frame_groupings.frame_group_details = frame_group_details

            # save
            new_lec_gaze_frame_groupings.save()


            return Response({
                "frame_landmarks": frame_landmarks,
                "frame_group_percentages": frame_group_percentages,
                "gaze_labels": gaze_labels
            })


# =====OTHERS=====
# this API will retrieve the respective lecturer video name
class GetLecturerRecordedVideo(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        subject = request.query_params.get('subject')
        date = request.query_params.get('date')

        # retrieve data
        lec_recorded_video = LectureRecordedVideo.objects.filter(lecturer_id=lecturer, subject__subject_code=subject, lecturer_date=date)
        lec_recorded_video_ser = LectureRecordedVideoSerializer(lec_recorded_video, many=True)
        lec_recorded_video_data = lec_recorded_video_ser.data[0]

        # extract the lecturer video name
        video_name = lec_recorded_video_data['lecture_video_name']

        print('lecturer recorded video name: ', video_name)

        # return the response
        return Response({
            "video_name": video_name
        })


# this API will get lecture activity correlations
class GetLectureActivityCorrelations(APIView):

    def get(self, request):
        # this variable defines the number of dates to be considered for activity correlations
        option = request.query_params.get('option')
        # the lecturer id
        lecturer = request.query_params.get('lecturer')
        int_option = int(option)

        # get the current date
        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        # subtract the current date by the time period given
        previous_date = current_date - option_date

        # this list contains the student activities for each lecture
        individual_lec_activities = []
        # this list will contain the student activity-lecturer posture activity correlations
        activity_correlations = []

        # retrieving lecture activities
        lec_activity = LectureActivity.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        if len(lec_activity) > 0:
            isRecordFound = True
            activity_serializer = LectureActivitySerializer(lec_activity, many=True)
            activity_data = activity_serializer.data
            _, individual_lec_activities, _ = ar.get_student_activity_summary_for_period(activity_data)


        # retrieving lecturer recorded activities
        lec_recorded_activity = LecturerVideoMetaData.objects.filter(
            lecturer_video_id__lecturer_date__gte=previous_date,
            lecturer_video_id__lecturer_date__lte=current_date,
            lecturer_video_id__lecturer=lecturer
        )

        if len(lec_recorded_activity) > 0:
            lec_recorded_activity_ser = LecturerVideoMetaDataSerializer(lec_recorded_activity, many=True)
            lec_recorded_activity_data = lec_recorded_activity_ser.data


            activity_correlations = ar.get_activity_correlations(individual_lec_activities, lec_recorded_activity_data)



        return Response({
            "correlations": activity_correlations
        })


# this API will get lecture emotion correlations
class GetLectureEmotionCorrelations(APIView):

    def get(self, request):
        option = request.query_params.get('option')
        lecturer = request.query_params.get('lecturer')
        int_option = int(option)

        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        previous_date = current_date - option_date

        individual_lec_emotions = []
        emotion_correlations = []

        # retrieving lecture activities
        lec_emotion = LectureEmotionReport.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        # if there are lecture emotions
        if len(lec_emotion) > 0:
            emotion_serializer = LectureEmotionSerializer(lec_emotion, many=True)
            emotion_data = emotion_serializer.data
            _, individual_lec_emotions, _ = ed.get_student_emotion_summary_for_period(emotion_data)


        # retrieving lecturer recorded activities
        lec_recorded_activity = LecturerVideoMetaData.objects.filter(
            lecturer_video_id__lecturer_date__gte=previous_date,
            lecturer_video_id__lecturer_date__lte=current_date,
            lecturer_video_id__lecturer=lecturer
        )

        # if there are any recorded lectures
        if len(lec_recorded_activity) > 0:
            lec_recorded_activity_ser = LecturerVideoMetaDataSerializer(lec_recorded_activity, many=True)
            lec_recorded_activity_data = lec_recorded_activity_ser.data

            emotion_correlations = ed.get_emotion_correlations(individual_lec_emotions, lec_recorded_activity_data)


        return Response({
            "correlations": emotion_correlations
        })


# this API will get lecture gaze correlations
class GetLectureGazeCorrelations(APIView):

    def get(self, request):
        option = request.query_params.get('option')
        lecturer = request.query_params.get('lecturer')
        int_option = int(option)


        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        previous_date = current_date - option_date

        individual_lec_gaze = []
        gaze_correlations = []

        # retrieving lecture activities
        lec_gaze = LectureGazeEstimation.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        # if there are gaze estimations
        if len(lec_gaze) > 0:
            gaze_serializer = LectureGazeEstimationSerializer(lec_gaze, many=True)
            gaze_data = gaze_serializer.data
            _, individual_lec_gaze, _ = hge.get_student_gaze_estimation_summary_for_period(gaze_data)

        # retrieving lecturer recorded activities
        lec_recorded_activity = LecturerVideoMetaData.objects.filter(
            lecturer_video_id__lecturer_date__gte=previous_date,
            lecturer_video_id__lecturer_date__lte=current_date,
            lecturer_video_id__lecturer=lecturer
        )

        # if there are any recorded lectures
        if len(lec_recorded_activity) > 0:
            lec_recorded_activity_ser = LecturerVideoMetaDataSerializer(lec_recorded_activity, many=True)
            lec_recorded_activity_data = lec_recorded_activity_ser.data

            # find the correlations between lecture gaze estimations and recorded lecture
            gaze_correlations = hge.get_gaze_correlations(individual_lec_gaze, lec_recorded_activity_data)


        return Response({
            "correlations": gaze_correlations
        })


# this class will handle the student activity-emotion correlations
class GetStudentActivityEmotionCorrelations(APIView):

    def get(self, request):
        # get the day option
        option = request.query_params.get('option')
        # get the lecturer id
        lecturer = request.query_params.get('lecturer')
        int_option = int(option)
        # initialize the student behavior count
        student_behavior_count = 0


        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        # get the actual date
        previous_date = current_date - option_date

        # initialize the lists
        individual_lec_activities = []
        individual_lec_emotions = []
        activity_emotion_correlations = []

        # retrieving lecture activities
        lec_activity = LectureActivity.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        # retrieving lecture emotions
        lec_emotion = LectureEmotionReport.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )


        # if there are lecture activities
        if len(lec_activity) > 0:
            student_behavior_count += 1
            activity_serializer = LectureActivitySerializer(lec_activity, many=True)
            activity_data = activity_serializer.data
            _, individual_lec_activities, _ = ar.get_student_activity_summary_for_period(activity_data)

        # if there are lecture emotions
        if len(lec_emotion) > 0:
            student_behavior_count += 1
            emotion_serializer = LectureEmotionSerializer(lec_emotion, many=True)
            emotion_data = emotion_serializer.data
            _, individual_lec_emotions, _ = ed.get_student_emotion_summary_for_period(emotion_data)


        # if both student activity, emotion are available
        if student_behavior_count == 2:

            # find the correlations between student activity and gaze estimations
            activity_emotion_correlations = sbp.calculate_student_activity_emotion_correlations(individual_lec_activities, individual_lec_emotions)


        return Response({
            "correlations": activity_emotion_correlations
        })


# this class will handle the student activity-emotion correlations
class GetStudentActivityGazeCorrelations(APIView):

    def get(self, request):
        # get the day option
        option = request.query_params.get('option')
        # get the lecturer id
        lecturer = request.query_params.get('lecturer')
        int_option = int(option)
        # initialize the student behavior count
        student_behavior_count = 0


        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        # get the actual date
        previous_date = current_date - option_date

        # initialize the lists
        individual_lec_activities = []
        individual_lec_gaze = []
        activity_gaze_correlations = []


        # retrieving lecture gaze estimations
        lec_gaze = LectureGazeEstimation.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )


        # retrieving lecture activities
        lec_activity = LectureActivity.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )


        # if there are lecture activities
        if len(lec_activity) > 0:
            student_behavior_count += 1
            activity_serializer = LectureActivitySerializer(lec_activity, many=True)
            activity_data = activity_serializer.data
            _, individual_lec_activities, _ = ar.get_student_activity_summary_for_period(activity_data)


        # if there are gaze estimations
        if len(lec_gaze) > 0:
            student_behavior_count += 1
            gaze_serializer = LectureGazeEstimationSerializer(lec_gaze, many=True)
            gaze_data = gaze_serializer.data
            _, individual_lec_gaze, _ = hge.get_student_gaze_estimation_summary_for_period(gaze_data)


        # if there are any recorded lectures
        if student_behavior_count == 2:

            # find the correlations between student activity and gaze estimations
            activity_gaze_correlations = sbp.calculate_student_activity_gaze_correlations(individual_lec_activities, individual_lec_gaze)


        return Response({
            "correlations": activity_gaze_correlations
        })


# this class will handle the student emotion-gaze correlations
class GetStudentEmotionGazeCorrelations(APIView):

    def get(self, request):
        # get the day option
        option = request.query_params.get('option')
        # get the lecturer id
        lecturer = request.query_params.get('lecturer')
        int_option = int(option)
        # initialize the student behavior count
        student_behavior_count = 0


        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        # get the actual date
        previous_date = current_date - option_date

        # initialize the lists
        individual_lec_emotions = []
        individual_lec_gaze = []
        emotion_gaze_correlations = []


        # retrieving lecture gaze estimations
        lec_gaze = LectureGazeEstimation.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        # retrieving lecture emotions
        lec_emotion = LectureEmotionReport.objects.filter(
            lecture_video_id__date__gte=previous_date,
            lecture_video_id__date__lte=current_date,
            lecture_video_id__lecturer=lecturer
        )

        # if there are lecture emotions
        if len(lec_emotion) > 0:
            student_behavior_count += 1
            emotion_serializer = LectureEmotionSerializer(lec_emotion, many=True)
            emotion_data = emotion_serializer.data
            _, individual_lec_emotions, _ = ed.get_student_emotion_summary_for_period(emotion_data)

        # if there are gaze estimations
        if len(lec_gaze) > 0:
            student_behavior_count += 1
            gaze_serializer = LectureGazeEstimationSerializer(lec_gaze, many=True)
            gaze_data = gaze_serializer.data
            _, individual_lec_gaze, _ = hge.get_student_gaze_estimation_summary_for_period(gaze_data)



        # if there are any recorded lectures
        if student_behavior_count == 2:

            # find the correlations between student activity and gaze estimations
            emotion_gaze_correlations = sbp.calculate_student_emotion_gaze_correlations(individual_lec_emotions, individual_lec_gaze)


        return Response({
            "correlations": emotion_gaze_correlations
        })


##### BATCH PROCESS SECTION #####

# perform the student behavior analysis as a batch process
class BatchProcess(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        video_id = request.query_params.get('video_id')

        return Response({
            "response": True
        })


# this API will check whether the lecture activity frame groupings exist
class CheckStudentBehaviorAvailability(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        print('video name: ', video_name)

        # retrieve the 'MongoDbJobStore' instance
        jobs = MongoDBJobStore().get_all_jobs()

        print('jobs: ', jobs)

        # initialize the variables
        isActivityExist = False
        isEmotionExist = False
        isGazeExist = False

        # if there are scheduled jobs
        if len(jobs) > 0:

            # retrieve the activity frame groupings
            isActivityExist = LectureActivityFrameGroupings.objects.filter(lecture_activity_id__lecture_video_id__video_name=video_name).exists()
            # retrieve the emotion frame groupings
            isEmotionExist = LectureEmotionFrameGroupings.objects.filter(lecture_emotion_id__lecture_video_id__video_name=video_name).exists()
            # retrieve the gaze frame groupings
            isGazeExist = LectureGazeFrameGroupings.objects.filter(lecture_gaze_id__lecture_video_id__video_name=video_name).exists()

        else:

            isActivityExist = True
            isEmotionExist = True
            isGazeExist = True
            # isActivityExist = bool(Random().randint(0,2))
            # isEmotionExist = bool(Random().randint(0,2))
            # isGazeExist = bool(Random().randint(0,2))

        return Response({
            "isActivityExist": isActivityExist,
            "isEmotionExist": isEmotionExist,
            "isGazeExist": isGazeExist
        })

# this API will perform some random task (delete later)
class TestRandom(APIView):

    def get(self, request):

        random = Random().randint(0, 100)

        return Response({
            "response": random
        })


# this API will display the upcoming lectures for the lecturer (temporary API)
class DisplayUpcomingLecturesAPI(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        lecturer = int(lecturer)
        cur_date = datetime.datetime.now().date()
        cur_time = datetime.datetime.now().time()

        eligible_start_time = ''
        eligible_end_time = ''
        subject_id = 0
        subject_name = ''
        subject_code = ''

        # retrieve the faculty timetable
        faculty_timetable = FacultyTimetable.objects.all()

        # serialize the timetable
        faculty_timetable_serialized = FacultyTimetableSerializer(faculty_timetable, many=True)

        # get the serialized timetable data
        faculty_timetable_serialized_data = faculty_timetable_serialized.data

        # iterate through the serialized timetable data
        for timetable in faculty_timetable_serialized_data:

            # get the 'timetable' field
            daily_timetable = timetable['timetable']

            # iterate through the 'timetable' field
            for day_timetable in daily_timetable:

                # get the 'time_slots' field for a given day
                time_slots = day_timetable['time_slots']

                # iterate through the time slots
                for time_slot in time_slots:

                    # if the lecturer is the currently logged in lecturer
                    if lecturer == time_slot['lecturer']['id']:

                        # find the upcoming lecture for the logged-in lecturer
                        if cur_date == day_timetable['date']:

                            # get the start and end times
                            start_time = time_slot['start_time']
                            end_time = time_slot['end_time']

                            start_time_list = str(start_time).split(":")

                            start_time_date = datetime.datetime.now().replace(hour=int(start_time_list[0]), minute=int(start_time_list[1]), second=int(start_time_list[2]))

                            end_time_list = str(end_time).split(":")

                            end_time_date = datetime.datetime.now().replace(hour=int(end_time_list[0]), minute=int(end_time_list[1]), second=int(end_time_list[2]))

                            # check for the upcoming time slot
                            if (start_time_date.time() > cur_time):
                                eligible_start_time = start_time_date.time()
                                eligible_end_time = end_time_date.time()
                                subject_id = time_slot['subject']['id']
                                subject_name = time_slot['subject']['name']
                                subject_code = time_slot['subject']['subject_code']




        return Response({
            "start_time": eligible_start_time,
            "end_time": eligible_end_time,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "subject_code": subject_code,
        })

# this API will handle all the batch processes and video/audio saving to the system
class AutomationProcess(APIView):

    def get(self, request):

        return Response({
            "response": "This API will be used for Automation process"
        })

    def post(self, request):

        processed = False

        try :

            lecturer = request.data['lecturer']
            subject = request.data['subject']
            subject_code = request.data['subject_code']
            video_length = request.data['video_length']

            # processed = ap.automation_process(lecturer=lecturer, subject=subject, subject_code=subject_code, video_length=video_length)
            # run the scheduler
            scheduler = task_scheduler(lecturer=lecturer, subject=subject, subject_code=subject_code, video_length=video_length)

            processed = True

            return Response({
                "is_processed": processed,
            })

        except Exception as exc:
            print('Exception: ', exc)
            return Response({
                "is_processed": processed,
            })