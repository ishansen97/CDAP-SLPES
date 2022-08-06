from rest_framework import serializers

from FirstApp.MongoModels import Lecturer, Subject
from FirstApp.serializers import LecturerSerializer, SubjectSerializer
from LectureSummarizingApp.models import LectureAudioSummary
from .models import RegisterTeacher, LecturerActivityFrameRecognitions
from .models import LecturerAudioText, LecturerVideoMetaData, LecturerVideo, LectureRecordedVideo
from FirstApp.logic import id_generator as ig

import datetime


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

    # this method will validate the input data
    def to_internal_value(self, data):
        lecturer = None
        subject = None

        lecturer_data = data.get('lecturer')
        subject_data = data.get('subject')

        # serialize the lecturer data
        lecturer = Lecturer.objects.filter(id=lecturer_data)
        subject = Subject.objects.filter(id=subject_data)

        lecturer_ser_data = LecturerSerializer(lecturer, many=True).data[0]
        subject_ser_data = SubjectSerializer(subject, many=True).data[0]

        # retrieve the last lecture video details
        last_lec_video = LectureRecordedVideo.objects.order_by('lecture_video_id').last()
        # create the next lecture video id
        new_lecture_video_id = ig.generate_new_id(last_lec_video.lecture_video_id)

        # if both subject and lecturer details are available
        if len(lecturer) == 1 & len(subject) == 1:
            str_video_length = data.get('lecture_video_length')
            video_length_parts = str_video_length.split(':')
            video_length = datetime.timedelta(minutes=int(video_length_parts[0]),
                                              seconds=int(video_length_parts[1]),
                                              milliseconds=int(video_length_parts[2]))

        # this data will be passed as validated data
        validated_data = {
            'lecture_video_id': new_lecture_video_id,
            'lecturer': lecturer_ser_data,
            'subject': subject_ser_data,
            'lecturer_date': data.get('lecturer_date'),
            'lecture_video_name': data.get('lecture_video_name'),
            'lecture_video_length': video_length
        }

        return super(LectureRecordedVideoSerializer, self).to_internal_value(validated_data)

    # this method will override the 'create' method
    def create(self, validated_data):
        lecturer = None
        subject = None

        lecturer_data = validated_data.pop('lecturer')
        subject_data = validated_data.pop('subject')

        # serialize the lecturer data
        lecturer = Lecturer.objects.filter(id=lecturer_data)
        subject = Subject.objects.filter(id=subject_data)

        # retrieve the last lecture video details
        last_lec_video = LectureRecordedVideo.objects.order_by('lecture_video_id').last()
        # create the next lecture video id
        new_lecture_video_id = ig.generate_new_id(last_lec_video.lecture_video_id)

        # if both subject and lecturer details are available
        if len(lecturer) == 1 & len(subject) == 1:
            str_video_length = validated_data.pop('lecture_video_length')
            video_length_parts = str_video_length.split(':')
            video_length = datetime.timedelta(minutes=int(video_length_parts[0]),
                                              seconds=int(video_length_parts[1]),
                                              milliseconds=int(video_length_parts[2]))

            lecture_video, created = LectureRecordedVideo.objects.update_or_create(
                lecture_video_id=new_lecture_video_id,
                lecturer=lecturer[0],
                subject=subject[0],
                lecturer_date=validated_data.pop('lecturer_date'),
                lecture_video_name=validated_data.pop('lecture_video_name'),
                lecture_video_length=video_length
            )

            # retrieve the created object
            created_lecture_video = LectureRecordedVideo.objects.filter(lecture_video_id=lecture_video)
            create_lecture_video_ser = LectureRecordedVideoSerializer(created_lecture_video, many=True)
            create_lecture_video_ser_data = create_lecture_video_ser.data

            return create_lecture_video_ser_data

        return None


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
