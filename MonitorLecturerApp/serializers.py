from rest_framework import serializers

from FirstApp.serializers import LecturerSerializer, SubjectSerializer
from LectureSummarizingApp.models import LectureAudioSummary
from .models import RegisterTeacher, LecturerActivityFrameRecognitions
from .models import LecturerAudioText, LecturerVideoMetaData, LecturerVideo, LectureRecordedVideo


class RegisterTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterTeacher
        fields = {'fName', 'lName', 'subject', 'email', 'password'}


class LecturerVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturerVideo
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


class LecturerVideoMetaDataSerializer(serializers.ModelSerializer):

    lecturer_video_id = LectureRecordedVideoSerializer()

    class Meta:
        model = LecturerVideoMetaData
        fields = '__all__'



# lecture activity frame recognition serializer
class LecturerActivityFrameRecognitionsSerializer(serializers.ModelSerializer):

    lecturer_meta_id = LecturerVideoMetaDataSerializer()
    frame_recognition_details = serializers.SerializerMethodField()

    # this method will be used to serialize the 'frame_recogition_details' field
    def get_frame_recognition_details(self, obj):

        return_data = []

        for frame_recognition in obj.frame_recognition_details:
            recognition = {}

            recognition["frame_name"] = frame_recognition.frame_name
            recognition["sitting_perct"] = frame_recognition.sitting_perct
            recognition["standing_perct"] = frame_recognition.standing_perct
            recognition["walking_perct"] = frame_recognition.walking_perct

            return_data.append(recognition)

        # return the data
        return return_data


    class Meta:
        model = LecturerActivityFrameRecognitions
        fields = '__all__'

