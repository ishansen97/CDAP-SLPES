from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .models import LectureAudio, LectureAudioNoiseRemoved, LectureSpeechToText, LectureAudioSummary, LectureNotices
from .serializer import LectureAudioSerializer, LectureAudioNoiseRemovedSerializer, LectureAudioSummarySerializer, \
    LectureSpeechToTextSerializer, LectureNoticesSerializer

def lectureRecord(request):

    lecture_audio = LectureAudio.objects.all()
    lecture_audio_ser = LectureAudioSerializer(lecture_audio, many=True)

    print('lecture record data: ', lecture_audio_ser.data)

    return render(request, "LectureSummarizationApp/RecordLecture.html")

# Views used in Lecture Summarization

def summarization(request):

    lec_audio = LectureAudio.objects.all()
    lec_audio_serializer = LectureAudioSerializer(lec_audio, many=True)
    data = lec_audio_serializer.data

    lec_noiseless_audio = LectureAudioNoiseRemoved.objects.all()
    lec_noiseless_audio_ser = LectureAudioNoiseRemovedSerializer(lec_noiseless_audio, many=True)
    noiseless_data = lec_noiseless_audio_ser.data

    lec_text = LectureSpeechToText.objects.all()
    lec_text_ser = LectureSpeechToTextSerializer(lec_text, many=True)
    lecture_text_data = lec_text_ser.data

    lec_summary = LectureAudioSummary.objects.all()
    lec_summary_ser = LectureAudioSummarySerializer(lec_summary, many=True)
    lec_summary_data = lec_summary_ser.data

    lec_notice = LectureNotices.objects.all()
    lec_notice_ser = LectureNoticesSerializer(lec_notice, many=True)
    lec_notice_data = lec_notice_ser.data


    return render(request, "LectureSummarizingApp/summarization.html", {"lec_audio_data": data, "noiseless_data": noiseless_data,"lecture_text_data": lecture_text_data, "lec_summary_data" : lec_summary_data, "lec_notice_data":lec_notice_data})


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
            serializer = LectureNoticesSerializer(lecture_notice_id, many=True)
            return Response(serializer.data)

        def post(self, request):
            LectureNotices(
                lecture_notice_id=request.data["lecture_notice_id"],
                lecture_audio_id=request.data["lecture_audio_id"],
                notice_text=request.data["notice_text"]
            ).save()
            return Response({"response": request.data})

