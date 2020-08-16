from rest_framework.views import APIView
from rest_framework.response import Response
from . logic import classroom_activity, text_analysis as ta


class ActivityRecognitionAPI(APIView):

    def get(self, request):
        video_name = request.query_params.get('video_name')
        percentages = classroom_activity.activity_recognition(video_name)
        return Response({"response": percentages})

    def post(self, request):
        pass


# this class will be used to retrieve audio analysis for a lecture
class GetLectureAudioAnalysis(APIView):

    def get(self, request):
        analysis = ta.run()

        return Response({
            "response":analysis
        })