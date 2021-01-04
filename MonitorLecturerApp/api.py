from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from LectureSummarizingApp.models import LectureAudioSummary
from LectureSummarizingApp.serializer import LectureAudioSummarySerializer
from . logic import classroom_activity, text_analysis as ta
from .models import LecturerVideo, LecturerAudioText, LecturerVideoMetaData, LectureRecordedVideo
from .serializers import *

import datetime


##### LECTURER VIDEO SECTION #####

# this API will handle basic lecturer video retrieval/saving
class LecturerVideoAPI(APIView):

    def get(self, request):
        lecturer_videos = LectureRecordedVideo.objects.all()
        lecturer_videos_ser = LectureRecordedVideoSerializer(lecturer_videos, many=True)
        lecturer_videos_ser_data = lecturer_videos_ser.data

        return Response({
            "response": lecturer_videos_ser_data
        })

    def post(self, request):

        serializer = LectureRecordedVideoSerializer(data=request.data)

        if serializer.is_valid(raise_exception=ValueError):
            # serializer.create(validated_data=request.data)
            serializer.create(validated_data=request.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


##### END OF LECTURER VIDEO SECTION #####


##### LECTURER ACTIVITY SECTION #####
class ActivityRecognitionAPI(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # retrieve the lecturer video details with the video name
        lec_video = LectureRecordedVideo.objects.filter(lecture_video_name=video_name)
        lec_video_ser = LectureRecordedVideoSerializer(lec_video, many=True)
        lec_video_data = lec_video_ser.data
        percentages = classroom_activity.activity_recognition(video_name)

        # saving to the db
        LecturerVideoMetaData(
            lecturer_video_id_id=lec_video_data[0]['id'],
            seated_count=percentages["sitting_perct"],
            standing_count=percentages["standing_perct"],
            walking_count=percentages["walking_perct"]
        ).save()

        return Response({"response": percentages})

    def post(self, request):
        pass


# this method will retrieve the lecturer video meta data results
class GetLectureVideoResultsAPI(APIView):

    def get(self, request):
        video_id = request.query_params.get('video_id')
        int_video_id = int(video_id)

        # retrieve from the db
        video_meta_data = LecturerVideoMetaData.objects.filter(lecturer_video_id_id=int_video_id)
        video_meta_data_ser = LecturerVideoMetaDataSerializer(video_meta_data, many=True)
        video_meta_data_processed = video_meta_data_ser.data
        percentages = {}

        for meta_data in video_meta_data_processed:
            percentages["sitting_perct"] = meta_data["seated_count"]
            percentages["standing_perct"] = meta_data["standing_count"]
            percentages["walking_perct"] = meta_data["walking_count"]



        return Response({
            "response": percentages
        })

# this API will process lecturer video frame recognitions
class ProcessLecturerFrameRecognitionsAPI(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        frame_recognitions, fps = classroom_activity.save_frame_recognition(video_name)

        int_fps = int(fps)

        # print('frame recognitions: ', frame_recognitions)

        return Response({
            "frame_recognitions": frame_recognitions,
            "fps": fps
        })


##### END OF LECTURER ACTIVITY SECTION #####


# class ActivityRecognitionAPI(APIView):
#
#     def get(self, request):
#         video_name = request.query_params.get('video_name')
#         percentages = classroom_activity.activity_recognition(video_name)
#         return Response({"response": percentages})
#
#     def post(self, request):
#         pass


# this class will be used to retrieve audio analysis for a lecture
class GetLectureAudioAnalysis(APIView):

    def get(self, request):
        lec_audio_id = request.query_params.get("audio_id")
        int_audio_id = int(lec_audio_id)

        print('audio id: ', int_audio_id)

        # all_lec_audio_summary

        lec_audio_summary = LectureAudioSummary.objects.filter(lecture_audio_id=int_audio_id)
        lec_audio_summary_serializer = LectureAudioSummarySerializer(lec_audio_summary, many=True)
        audio_summary_data = lec_audio_summary_serializer.data
        lec_audio_summary_id = 0

        print('lec audio summary: ', len(audio_summary_data))

        for audio in audio_summary_data:
            lec_audio_summary_id = audio['id']

        # retrieve summary text data
        lec_audio_text = LecturerAudioText.objects.filter(lecturer_audio_original_text__id=lec_audio_summary_id)
        lec_audio_text_serializer = LecturerAudioTextSerializer(lec_audio_text, many=True)
        lec_audio_text_data = lec_audio_text_serializer.data

        print('lec audio text data: ', len(lec_audio_text_data))

        audio_text = []

        if len(lec_audio_text_data) > 0:
            audio_text = lec_audio_text_data[0]

        print('audio text: ', audio_text)

        return Response({
            "response":audio_text
        })


# test api
class TestAPI(APIView):

    # retrieve all the details
    def get(self, request):
        lecturer_videos = LecturerVideo.objects.all()
        lecturer_vidoe_serializer = LecturerVideoSerializer(lecturer_videos, many=True)
        data = lecturer_vidoe_serializer.data

        return Response({
            "response": data
        })

    def post(self, request):

        name = request.data['name']
        path = request.data['path']
        duration = request.data['duration']
        hours = request.data['hours']
        minutes = request.data['minutes']
        seconds = request.data['seconds']

        # create the LecturerVideo details
        LecturerVideo(
            id=2,
            name=name,
            path=path,
            duration=duration,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ).save()


        return Response({
            "response": "Success"
        })


# this API will retrieve lecture audio text details
class LectureAudioTextAPI(APIView):

    def get(self, request):
        lecture_audio_text = LecturerAudioText.objects.all()
        lecture_audio_text_serializer = LecturerAudioTextSerializer(lecture_audio_text, many=True)

        data = lecture_audio_text_serializer.data

        return Response({
            "response": data
        })


# this API will save the lecture audio analysis
class ProcessLectureAudioAnalysis(APIView):

    def get(self, request):

        # lec_audio_text = ta.run()

        # (this is temporary)
        lec_audio_text = {
            'num_of_words': 5000,
            'lexical_count': 300,
            'non_lexical_count': 40
        }

        last_lec_audio_text_id = LecturerAudioText.objects.order_by('lecturer_audio_text_id').last()
        new_lec_audio_text_id = "LAT001" if (last_lec_audio_text_id is None) else ig.generate_new_id(
            last_lec_audio_text_id.lecturer_audio_text_id)

        # retrieve the lecture audio summary object (temporary)
        lecture_audio_summary = LectureAudioSummary.objects.filter(lecture_audio_summary_id='LAU004_sum')[0]

        # save the lecture audio text object
        LecturerAudioText(
            lecturer_audio_text_id=new_lec_audio_text_id,
            lecturer_audio_text_wordcount=lec_audio_text['num_of_words'],
            lecturer_audio_text_lexical_wordcount=lec_audio_text['lexical_count'],
            lecturer_audio_text_non_lexical_wordcount=lec_audio_text['non_lexical_count'],
            lecturer_audio_text_status='Average',
            lecturer_audio_original_text=lecture_audio_summary
        ).save()


        return Response({
            "response": "success"
        }, status=status.HTTP_201_CREATED)


# this API will retrieve lectuer audio summary for given period
class LecturerAudioSummaryPeriodAPI(APIView):

    def get(self, request):
        print('hello')
        option = request.query_params.get('option')
        int_option = int(option)

        # i cheated here (remove this once you have many recent records) - ok
        int_option = 150

        isRecordFound = False
        lec_audio_text_stats = []
        labels = []

        current_date = datetime.datetime.now().date()
        option_date = datetime.timedelta(days=int_option)

        previous_date = current_date - option_date

        lec_audio_text = LecturerAudioText.objects.filter(
            lecturer_audio_original_text__lecture_audio_id__lecturer_date__gte=previous_date,
            lecturer_audio_original_text__lecture_audio_id__lecturer_date__lte=current_date
        )

        # if there are records
        if len(lec_audio_text) > 0:
            isRecordFound = True
            lec_audio_text_ser = LecturerAudioTextSerializer(lec_audio_text, many=True)
            lec_audio_text_data = lec_audio_text_ser.data
            lec_audio_text_stats, labels = ta.get_lecturer_audio_summary_for_period(lec_audio_text_data)



        return Response({
            "statistics": lec_audio_text_stats,
            "labels": labels,
            "isRecordFound": isRecordFound
        })


# this section is for student and lecturer behavior integration
class StudentLecturerIntegratedAPI(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')

        # finding the existence of Lecture activity frame recognition record
        isExist = LecturerActivityFrameRecognitions.objects.filter(
            lecturer_meta_id__lecturer_video_id__lecture_video_name=video_name).exists()

        if (isExist):
            lecture_activity_frame_recognitions = LecturerActivityFrameRecognitions.objects.filter(
                lecturer_meta_id__lecturer_video_id__lecture_video_name=video_name)
            lecture_activity_frame_recognitions_ser = LecturerActivityFrameRecognitionsSerializer(
                lecture_activity_frame_recognitions, many=True)
            lecture_activity_frame_recognitions_data = lecture_activity_frame_recognitions_ser.data[0]

            frame_detections = lecture_activity_frame_recognitions_data['frame_recognition_details']
            fps = lecture_activity_frame_recognitions_data['fps']
            int_fps = int(fps)

            return Response({
                "frame_recognitions": frame_detections,
                "fps": fps
            })

        else:

            # frame_recognitions = classroom_activity.get_lecturer_activity_for_frames(video_name)
            frame_recognitions, fps = classroom_activity.save_frame_recognition(video_name)

            int_fps = int(fps)

            # print('frame recognitions: ', frame_recognitions)

            return Response({
                "frame_recognitions": frame_recognitions,
                "fps": fps
            })

