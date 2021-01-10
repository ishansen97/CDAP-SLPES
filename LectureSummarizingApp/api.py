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
from .ExtractKeySentences import GetLectureNotice
from .Summary import LectureSummary
from .noise import noise_removal
from .speech_to_text import speech_to_text
from .voice_recorder import AudioRecorder


class LectureAudioAPI(APIView):

    def get(self,request):
        return Response({
            "response": Response.status_code
        })

    def post(self, request):
        lecture_audio = LectureAudio.objects.all().order_by('lecturer_date')
        lecture_audio_serializer = LectureAudioSerializer(lecture_audio, many=True)

        audio_list = LectureAudio.objects.order_by('lecture_audio_id').last()
        audio_name = request.data['audio_name']
        # id = int(request.query_params.get("id"))
        new_audio_id = generate_new_id(audio_list.lecture_audio_noise_removed_id)

        fake_duration = datetime.timedelta(minutes=00, seconds=10, milliseconds=00)
        AudioRecorder(audio_name)

        LectureAudio(
            lecture_audio_id=new_audio_id,
            lecture_audio_name =audio_name,
            lecture_audio_length = fake_duration,
            lecturer =request.data["lecturer"],
            subject = request.data["subject"]
        ).save()

        # get the created lecture audio instance
        created_lecture_audio = LectureAudio.objects.filter(lecture_audio_id=new_audio_id)

        return Response({
            "response": Response.status_code,
            "audio_id": int(created_lecture_audio[0].id)
        })


class AudioNoiseRemovedList(APIView):

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

        print('inside the noise removal api')

        noise_removal(audio_name)

        LectureAudioNoiseRemoved(
            lecture_audio_noise_removed_id=new_audio_noise_removed_id,
            lecture_audio_id_id=id,
            lecturer_date=current_date,
            lecture_audio_name=audio_name,
            lecture_audio_length=fake_duration
        ).save()

        print('ending the noise removal api')

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


class AudioToTextList(APIView):

    def get(self, request):
        #lecture_speech_to_text_id = LectureSpeechToText.objects.all()
        #serializer = LectureSpeechToTextSerializer(lecture_speech_to_text_id, many=True)
        audio_to_text_list = LectureSpeechToText.objects.order_by('lecture_speech_to_text_id').last()
        # return Response(serializer.data)

        speech_to_text_name = request.query_params.get("speech_to_text_name")

        print('file name: ', speech_to_text_name)
        id = int(request.query_params.get("id"))
        # id = request.query_params.get("id")


        # generate new id for speech to text file
        new_speech_to_text_id = "LST0001" if audio_to_text_list is None else generate_new_id(audio_to_text_list.lecture_speech_to_text_id)

        speech_to_text(speech_to_text_name)

        LectureSpeechToText(
            lecture_speech_to_text_id=new_speech_to_text_id,
            lecture_audio_id_id=id,
            audio_original_text=speech_to_text_name
        ).save()

        return Response({
            "response": Response.status_code
        })

    def post(self, request):
        LectureSpeechToText(
            lecture_speech_to_text_id=request.data["lecture_speech_to_text_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            audio_original_text=request.data["audio_original_text"],
        ).save()
        return Response({"response": request.data})


class LectureSummaryList(APIView):

    def get(self, request):
        lecture_audio_summary_id = LectureAudioSummary.objects.all()
        # serializer = LectureAudioSummarySerializer(lecture_audio_summary_id, many=True)
        # return Response(serializer.data)

        lecture_summary_list = LectureAudioSummary.objects.order_by('lecture_audio_summary_id').last()

        lecture_summary_name = request.query_params.get("lecture_summary_name")
        id = int(request.query_params.get("id"))

        # generate new id for summary
        lecture_summary_id = "LSUM0001" if lecture_summary_list is None else generate_new_id(lecture_summary_list.lecture_audio_summary_id)

        text, summary = LectureSummary(lecture_summary_name)

        LectureAudioSummary(
            lecture_audio_summary_id=lecture_summary_id,
            lecture_audio_id_id=id,
            audio_original_text=text,
            audio_summary=summary
        ).save()
        return Response({"response": Response.status_code})

    def post(self, request):
        LectureAudioSummary(
            lecture_speech_to_text_id=request.data["lecture_speech_to_text_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            audio_original_text=request.data["audio_original_text"],
            audio_summary=request.data["audio_summary"]
        ).save()
        return Response({"response": request.data})



class LectureNoticeList(APIView):

    def get(self, request):
        lecture_notice_id = LectureNotices.objects.all()
        # serializer = LectureNoticesSerializer(lecture_notice_id, many=True)
        # return Response(serializer.data)

        lecture_notice_list = LectureNotices.objects.order_by('lecture_notice_id').last()

        lecture_notice_name = request.query_params.get("lecture_notice_name")
        id = int(request.query_params.get("id"))

        # generate new id for notice
        notice_id = "LN0001" if lecture_notice_list is None else generate_new_id(lecture_notice_list.lecture_notice_id)

        text, sentences_with_word = GetLectureNotice(lecture_notice_name)

        LectureNotices(
            lecture_notice_id=notice_id,
            lecture_audio_id_id=id,
            notice_text=text
        ).save()
        return Response({"response": Response.status_code})



    def post(self, request):
        LectureNotices(
            lecture_notice_id=request.data["lecture_notice_id"],
            lecture_audio_id=request.data["lecture_audio_id"],
            notice_text=request.data["notice_text"]
        ).save()
        return Response({"response": request.data})


class TestMethod(APIView):

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

        print('inside the noise removal api')

        noise_removal(audio_name)

        LectureAudioNoiseRemoved(
            lecture_audio_noise_removed_id=new_audio_noise_removed_id,
            lecture_audio_id_id=id,
            lecturer_date=current_date,
            lecture_audio_name=audio_name,
            lecture_audio_length=fake_duration
        ).save()

        print('ending the noise removal api')

        return Response({
            "response": Response.status_code
        })

class TestMethod02(APIView):
    def get(self, request):
        # lecture_speech_to_text_id = LectureSpeechToText.objects.all()
        # serializer = LectureSpeechToTextSerializer(lecture_speech_to_text_id, many=True)
        audio_to_text_list = LectureSpeechToText.objects.order_by('lecture_speech_to_text_id').last()
        # return Response(serializer.data)

        speech_to_text_name = request.query_params.get("speech_to_text_name")

        print('file name: ', speech_to_text_name)
        id = int(request.query_params.get("id"))
        # id = request.query_params.get("id")

        # generate new id for speech to text file
        new_speech_to_text_id = "LST0001" if audio_to_text_list is None else generate_new_id(
            audio_to_text_list.lecture_speech_to_text_id)

        speech_to_text(speech_to_text_name)

        LectureSpeechToText(
            lecture_speech_to_text_id=new_speech_to_text_id,
            lecture_audio_id_id=id,
            audio_original_text=speech_to_text_name
        ).save()

        return Response({
            "response": Response.status_code
        })