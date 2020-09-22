from rest_framework.views import APIView
from rest_framework.response import Response

from LectureSummarizingApp.models import LectureAudio
from LectureSummarizingApp.serializer import LectureAudioSerializer

# this API will retrieve lecture audio details
class LectureAudioAPI(APIView):

    def get(self, request):
        lecture_audio = LectureAudio.objects.all()
        lecture_audio_serializer = LectureAudioSerializer(lecture_audio, many=True)

        data = lecture_audio_serializer.data

        return Response({
            "response": data
        })