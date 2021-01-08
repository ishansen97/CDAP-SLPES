from rest_framework.views import APIView
from rest_framework.response import Response

from FirstApp.logic.id_generator import generate_new_id
from LectureSummarizingApp.models import LectureAudio, LectureAudioNoiseRemoved, LectureSpeechToText, \
    LectureAudioSummary, LectureNotices
from LectureSummarizingApp.serializer import LectureAudioSerializer, LectureAudioNoiseRemovedSerializer, \
    LectureSpeechToTextSerializer, LectureAudioSummarySerializer, LectureNoticesSerializer

from . import speech_to_text as stt
from . import noiseRemove as nr

import datetime


# APIs used in Lecture Summarizing Component
from .noise import noise_removal


class LectureAudioAPI(APIView):

    def get(self, request):
        lecture_audio = LectureAudio.objects.all().order_by('lecturer_date')
        lecture_audio_serializer = LectureAudioSerializer(lecture_audio, many=True)
        return Response(lecture_audio_serializer.data)


class audioNoiseRemovedList(APIView):

    def get(self, request):
        # lecture_audio_noise_removed = LectureAudioNoiseRemoved.objects.all()
        # serializer = LectureAudioNoiseRemovedSerializer(lecture_audio_noise_removed, many=True)
        audio_noise_removed_list = LectureAudioNoiseRemoved.objects.order_by('lecture_audio_noise_removed_id').last()

        audio_name = request.query_params.get("audio_name")
        id = int(request.query_params.get("id"))


        current_date = datetime.datetime.now().date()

        fake_duration = datetime.timedelta(minutes=2, seconds=10, milliseconds=00)

        # generate new id for audio noise removed
        new_audio_noise_removed_id = generate_new_id(audio_noise_removed_list.lecture_audio_noise_removed_id)


        # nr.noise_removalll(video_name)
        noise_removal(audio_name)

        LectureAudioNoiseRemoved(
            lecture_audio_noise_removed_id=new_audio_noise_removed_id,
            lecture_audio_id_id=id,
            lecturer_date=current_date,
            lecture_audio_name=audio_name,
            lecture_audio_length=fake_duration
        ).save()

        return Response({
            "response": Response.status_code
        })

    def post(self, request):
        LectureAudioNoiseRemoved(
            lecture_audio_noise_removed_id=request.data["lecture_audio_noise_removed_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            lecturer_date=request.data["lecturer_date"],
            lecture_audio_name=request.data["lecture_audio_name"],
            lecture_audio_length=request.data["lecture_audio_length"]
        ).save()
        return Response({"response": request.data})


class audioToTextList(APIView):

    def get(self, request):
        lecture_speech_to_text_id = LectureSpeechToText.objects.all()
        serializer = LectureSpeechToTextSerializer(lecture_speech_to_text_id, many=True)
        # return Response(serializer.data)

        # video_name = request.query_params.get("video_name")
        #
        # print('video name: ', video_name)
        #
        # # nr.noise_removalll(video_name)
        # noise_removal(video_name)

        # stt.speech_to_text(video_name)

        return Response({
            "response": "successful"
        })

    def post(self, request):

        # video_name = request.data["video_name"]
        #
        # print('video name: ', video_name)
        #
        # stt.speech_to_text(video_name)

        LectureSpeechToText(
            lecture_speech_to_text_id=request.data["lecture_speech_to_text_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            audio_original_text=request.data["audio_original_text"]
        ).save()
        return Response({"response": request.data})


class lectureSummaryList(APIView):

    def get(self, request):
        lecture_audio_summary_id = LectureAudioSummary.objects.all()
        serializer = LectureAudioSummarySerializer(lecture_audio_summary_id, many=True)
        return Response(serializer.data)

    def post(self, request):



        LectureAudioSummary(
            lecture_speech_to_text_id=request.data["lecture_speech_to_text_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            audio_original_text=request.data["audio_original_text"],
            audio_summary=request.data["audio_summary"]
        ).save()
        return Response({"response": request.data})



class lectureNoticeList(APIView):

    def get(self, request):
        lecture_notice_id = LectureNotices.objects.all()
        serializer = LectureNoticesSerializer(lecture_notice_id, many=True)
        return Response(serializer.data)

    def post(self, request):
        LectureNotices(
            lecture_notice_id=request.data["lecture_notice_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            notice_text=request.data["notice_text"]
        ).save()
        return Response({"response": request.data})

