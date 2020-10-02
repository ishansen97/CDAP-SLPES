from rest_framework import serializers

from FirstApp.serializers import LecturerSerializer, SubjectSerializer
from LectureSummarizingApp.models import LectureAudioSummary
from .models import RegisterTeacher
from .models import LecturerAudioText, LecturerVideoMetaData, LecturerVideo, LectureRecordedVideo


class RegisterTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterTeacher
        fields = {'fName', 'lName', 'subject', 'email', 'password'}


class LecturerVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturerVideo
        fields = '__all__'

class LecturerVideoMetaDataSerializer(serializers.ModelSerializer):

    lecturer_video_id = LectureRecordedVideo()

    class Meta:
        model = LecturerVideoMetaData
        fields = '__all__'


class LecturerAudioTextSerializer(serializers.ModelSerializer):

    lecturer_audio_original_text = LectureAudioSummary()

    class Meta:
        model = LecturerAudioText
        fields = '__all__'


class LectureRecordedVideoSerializer(serializers.ModelSerializer):

    lecturer = LecturerSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = LectureRecordedVideo
        fields = '__all__'
