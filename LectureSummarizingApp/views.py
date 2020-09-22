from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .models import LectureAudio, LectureAudioNoiseRemoved, LectureSpeechToText, LectureAudioSummary, LectureNotices
from .serializer import LectureAudioSerializer, LectureAudioNoiseRemovedSerializer, LectureAudioSummarySerializer, \
    LectureSpeechToTextSerializer


# Create your views here.

def summarization(request):
    return render(request, "LectureSummarizingApp/summarization.html")


class audioList(APIView):

    def get(self, request):
        lecture_audio = LectureAudio.objects.all()
        serializer = LectureAudioSerializer(lecture_audio, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class audioNoiseRemovedList(APIView):

    def get(self, request):
        lecture_audio_noise_removed = LectureAudioNoiseRemoved.objects.all()
        serializer = LectureAudioNoiseRemovedSerializer(lecture_audio_noise_removed, many=True)
        return Response(serializer.data)

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
        return Response(serializer.data)

    def post(self, request):
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
            serializer = LectureSpeechToTextSerializer(lecture_notice_id, many=True)
            return Response(serializer.data)

        def post(self, request):
            LectureSpeechToText(
                lecture_notice_id=request.data["lecture_notice_id"],
                lecture_audio_id=request.data["lecture_audio_id"],
                notice_text=request.data["notice_text"]
            ).save()
            return Response({"response": request.data})