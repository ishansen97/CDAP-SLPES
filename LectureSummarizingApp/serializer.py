from rest_framework import serializers

from FirstApp.serializers import LecturerSerializer, SubjectSerializer
from . models import *


#serializers used in Lecture Summarizing Component
class LectureAudioSerializer(serializers.ModelSerializer):

    lecturer = LecturerSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = LectureAudio
        fields = '__all__'


class LectureAudioNoiseRemovedSerializer(serializers.ModelSerializer):
    lecture_audio_id = LectureAudioSerializer()

    class Meta:
        model = LectureAudioNoiseRemoved
        fields = '__all__'


class LectureSpeechToTextSerializer(serializers.ModelSerializer):
    lecture_audio_id = LectureAudioSerializer()

    class Meta:
        model = LectureSpeechToText
        fields = '__all__'


class LectureAudioSummarySerializer(serializers.ModelSerializer):
    lecture_audio_id = LectureAudioSerializer()

    class Meta:
        model = LectureAudioSummary
        fields = '__all__'


class LectureNoticesSerializer(serializers.ModelSerializer):
    lecture_audio_id = LectureAudioSerializer()

    class Meta:
        model = LectureNotices
        fields = '__all__'