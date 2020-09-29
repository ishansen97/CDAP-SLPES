from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .MongoModels import *
from rest_framework.views import *
from .ImageOperations import saveImage
from .logic import head_pose_estimation
from .logic import video_extraction
from .logic import activity_recognition as ar
from .logic import posenet_calculation as pc
from . import emotion_detector as ed
from .logic import id_generator as ig
from .logic import pdf_file_generator as pdf
from .logic import head_gaze_estimation as hge
from .models import Teachers, Video, VideoMeta, RegisterUser
from .MongoModels import *
from .serializers import *

import datetime


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
        serializer = LectureVideoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


class GetLectureVideoViewSet(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        date = request.query_params.get('date')
        index = int(request.query_params.get('index'))
        lecturer_video = LectureVideo.objects.filter(lecturer_id=lecturer, date=date)
        serializer = LectureVideoSerializer(lecturer_video, many=True)

        lecture_video_id = serializer.data[index]['lecture_video_id']
        print('lecture video id: ', lecture_video_id)
        activities = LectureActivity.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        isActivityFound = (len(activities) > 0)

        return Response({
            "response": serializer.data[index],
            "isActivityFound": isActivityFound
        })


# ACTIVITY
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
        lecture_video_name = request.query_params.get('lecture_video_name')
        # retrieve the extracted frames
        extracted = ar.getExtractedFrames(lecture_video_name)

        lecture_activities = LectureActivity.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        serializer = LectureActivitySerializer(lecture_activities, many=True)

        return Response({
            "response": serializer.data,
            "extracted": extracted
        })


# API to process lecture activity
class LectureActivityProcess(APIView):

    def get(self, request):
        video_name = request.query_params.get('lecture_video_name')
        video_id = request.query_params.get('lecture_video_id')
        percentages = ar.activity_recognition(video_name)
        self.activity(video_id, percentages)
        return Response({"response": True})

    def post(self, request):
        pass

    def activity(self, lec_video_id, percentages):
        lec_video = LectureVideo.objects.get(lecture_video_id=lec_video_id)
        last_lec_activity = LectureActivity.objects.order_by('lecture_activity_id').last()
        lec_video_serializer = LectureVideoSerializer(lec_video, many=True)
        new_lecture_activity_id = ig.generate_new_id(last_lec_activity.lecture_activity_id)

        # creating a new lecture activity
        LectureActivity(
            lecture_activity_id=new_lecture_activity_id,
            lecture_video_id=lec_video,
            talking_perct=percentages['talking_perct'],
            phone_perct=percentages['phone_perct'],
            listening_perct=percentages['listening_perct'],
            writing_perct=percentages['writing_perct']
        ).save()


class GetLectureActivityDetections(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        frame_name = request.query_params.get('frame_name')
        detections = ar.get_detections(video_name, frame_name)

        return Response({
            "detections": detections
        })


# the API class for getting student detections for a label
class GetLectureActvityDetectionsForLabel(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        label = request.query_params.get('label')
        labelled_detections, detected_people = ar.get_detections_for_label(video_name, label)

        return Response({
            "response": labelled_detections,
            "people": detected_people
        })


# the API class for getting students activity evaluations
class GetLectureActivityStudentEvaluation(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        labelled_detections, detected_people = ar.get_student_activity_evaluation(video_name)

        return Response({
            "response": labelled_detections,
            "people": detected_people
        })


# the API class to retrieve individual student evaluation (activity)
class GetLectureActivityIndividualStudentEvaluation(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        student_name = request.query_params.get('student_name')
        meta_data = ar.get_individual_student_evaluation(video_name, student_name)

        return Response({
            "response": meta_data
        })


# API to retrieve activity detections for frames
class GetLectureActivityRecognitionsForFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        frame_detections = ar.get_frame_activity_recognition(video_name)

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
        video_id = request.query_params.get('lecture_video_id')
        percentages = ed.detect_emotion(video_name)
        percentages.calcPercentages()
        self.save_emotion_report(video_id, percentages)
        return Response({"response": True})

    def post(self, request):
        pass

    def save_emotion_report(self, lec_video_id, percentages):
        lec_video = LectureVideo.objects.get(lecture_video_id=lec_video_id)
        lec_video_serializer = LectureVideoSerializer(lec_video, many=True)
        last_lec_emotion = LectureEmotionReport.objects.order_by('lecture_emotion_id').last()
        new_lecture_emotion_id = ig.generate_new_id(last_lec_emotion.lecture_emotion_id)

        # creating a new lecture emotion report
        LectureEmotionReport(
            lecture_emotion_id=new_lecture_emotion_id,
            lecture_video_id=lec_video,
            happy_perct=percentages.happy_perct,
            sad_perct=percentages.sad_perct,
            angry_perct=percentages.angry_perct,
            neutral_perct=percentages.neutral_perct,
            surprise_perct=percentages.surprise_perct
        ).save()


# to get a lecture emotion report
class GetLectureEmotionReportViewSet(APIView):

    def get(self, request):
        lecture_video_id = request.query_params.get('lecture_video_id')
        lecture_video_name = request.query_params.get('lecture_video_name')
        # retrieve the extracted frames
        extracted = ar.getExtractedFrames(lecture_video_name)

        lecture_emotions = LectureEmotionReport.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        serializer = LectureEmotionSerializer(lecture_emotions, many=True)

        print(len(serializer.data))

        return Response({
            "response": serializer.data,
            "extracted": extracted
        })


# the API class for getting students activity evaluations (emotions)
class GetLectureEmotionStudentEvaluations(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        labelled_detections, detected_people = ed.get_student_emotion_evaluations(video_name)

        return Response({
            "response": labelled_detections,
            "people": detected_people
        })


# the API class to retrieve individual student evaluation (emotion)
class GetLectureEmotionIndividualStudentEvaluation(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        student_name = request.query_params.get('student_name')
        meta_data = ed.get_individual_student_evaluation(video_name, student_name)
        serialized = VideoMetaSerializer(meta_data)

        return Response({
            "response": serialized.data
        })


# API to retrieve emotion detections for frames
class GetLectureEmotionRecognitionsForFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        frame_detections = ed.get_frame_emotion_recognition(video_name)

        return Response({
            "response": frame_detections
        })


##### POSE #####
class GetLectureVideoForPose(APIView):

    def get(self, request):
        lecturer = request.query_params.get('lecturer')
        date = request.query_params.get('date')
        index = int(request.query_params.get('index'))
        lecturer_video = LectureVideo.objects.filter(lecturer_id=lecturer, date=date)
        serializer = LectureVideoSerializer(lecturer_video, many=True)

        return Response({
            "response": serializer.data[index]
        })


# API to retrieve one lecture activity
class GetLectureVideoExtractedFrames(APIView):

    def get(self, request):
        lecture_video_id = request.query_params.get('lecture_video_id')
        lecture_video_name = request.query_params.get('lecture_video_name')
        # retrieve the extracted frames
        extracted = ar.getExtractedFrames(lecture_video_name)

        # lecture_activities = LectureActivity.objects.filter(lecture_video_id__lecture_video_id=lecture_video_id)
        # serializer = LectureActivitySerializer(lecture_activities, many=True)

        return Response({
            # "response": serializer.data,
            "extracted": extracted
        })


# API to retrieve individual student detections
class GetLectureVideoIndividualStudentFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        labelled_detections, detected_people = pc.get_pose_estimations(video_name)

        return Response({
            "response": labelled_detections,
            "people": detected_people
        })


# API to process pose estimation for an individual student
class ProcessIndividualStudentPoseEstimation(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self):
        pass

    # POST method
    def post(self, request):
        video_name = request.data['video_name']
        student = request.data['student']
        poses = request.data['poses']

        pc.calculate_pose_estimation_for_student(video_name, student, poses)
        return Response({
            "response": video_name
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
        lec_video = LectureVideo.objects.get(lecture_video_id=lec_video_id)
        last_lec_gaze = LectureGazeEstimation.objects.order_by('lecture_gaze_id').last()
        lec_video_serializer = LectureVideoSerializer(lec_video, many=True)
        new_lecture_gaze_id = "LG000001" if (last_lec_gaze is None) else ig.generate_new_id(
            last_lec_gaze.lecture_gaze_id)

        # creating a new lecture gaze estimation
        LectureGazeEstimation(
            lecture_gaze_id=new_lecture_gaze_id,
            lecture_video_id=lec_video,
            looking_up_and_right_perct=percentages['head_up_right_perct'],
            looking_up_and_left_perct=percentages['head_up_left_perct'],
            looking_down_and_right_perct=percentages['head_down_right_perct'],
            looking_down_and_left_perct=percentages['head_down_left_perct'],
            looking_front_perct=percentages['head_front_perct']
        ).save()


# the API to retrieve lecture gaze estimation
class GetLectureGazeEstimationViewSet(APIView):

    def get(self, request):
        lecture_video_id = request.query_params.get('lecture_video_id')
        lecture_video_name = request.query_params.get('lecture_video_name')
        # retrieve the extracted frames
        extracted = hge.getExtractedFrames(lecture_video_name)

        lecture_gaze_estimations = LectureGazeEstimation.objects.filter(
            lecture_video_id__lecture_video_id=lecture_video_id)
        serializer = LectureGazeEstimationSerializer(lecture_gaze_estimations, many=True)

        return Response({
            "response": serializer.data,
            "extracted": extracted
        })


# the API to retrieve Gaze estimation for frames
class GetLectureGazeEstimationForFrames(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        frame_detections, frame_rate = hge.get_lecture_gaze_esrimation_for_frames(video_name)

        return Response({
            "response": frame_detections,
            "frame_rate": frame_rate
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
        individual_lec_activties = []
        individual_lec_emotions = []
        activity_labels = []
        emotion_labels = []


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



        return Response({
            "activity_response": activity_percentages,
            "emotion_response": emotion_percentages,
            "individual_activities": individual_lec_activties,
            "individual_emotions": individual_lec_emotions,
            "activity_labels": activity_labels,
            "emotion_labels": emotion_labels,
            "isRecordFound": isRecordFound
        })
