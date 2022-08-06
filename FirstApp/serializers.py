"""

This file is responsible for implementing the serializer classes for each model classes

each serializer class extended by the djangorestframework's serializers class

there should be an inner class named "Meta" that needs to implemented inside each serializer class

there are two fields inside "Meta" class, as follows.
    model: the relevant model class that needs to be serialized
    fields: fields that need to be displayed when serializing the model class
        ('__all__' indicates that all the fields are required to be displayed)

"""





from rest_framework import serializers
from djongo import models
from .MongoModels import *
from . models import VideoMeta
from .logic import id_generator as ig
# from datetime import datetime as dt
import datetime


# lecture serializer
class LectureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lecture
        fields = '__all__'


# faculty serializer
class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        fields = '__all__'


# subject serializer
class SubjectSerializer(serializers.ModelSerializer):

    faculty = FacultySerializer()

    class Meta:
        model = Subject
        fields = '__all__'


    # overriding the create method
    def create(self, validated_data):

        faculty = None

        faculty_data = validated_data.pop('faculty')
        serialized_faculty = FacultySerializer(data=faculty_data)


        if (serialized_faculty.is_valid()):
            # faculty, faculty_created = Faculty.objects.get_or_create(defaults={}, faculty_id=serialized_faculty.data['faculty_id'])
            faculty = Faculty.objects.filter(faculty_id=serialized_faculty.data['faculty_id'])

            if (len(faculty) == 1):

                subject, created = Subject.objects.update_or_create(
                    faculty=faculty[0],
                    subject_code=validated_data.pop('subject_code'),
                    name=validated_data.pop('name'),
                    year=validated_data.pop('year')
                )

                print(type(subject.year))
                return subject

            return None

        return None



    def get_embedded_field(self, obj):
        return_data = None
        if type(obj.embedded_field) == list:
            embedded_list = []
            for item in obj.embedded_field:
                embedded_dict = item.__dict__
                for key in list(embedded_dict.keys()):
                    if key.startswith('_'):
                        embedded_dict.pop(key)
                embedded_list.append(embedded_dict)
            return_data = embedded_list
        else:
            embedded_dict = obj.embedded_field.__dict__
            for key in list(embedded_dict.keys()):
                if key.startswith('_'):
                    embedded_dict.pop(key)
            return_data = embedded_dict
        return return_data


# serializer for lecturer
class LecturerSerializer(serializers.ModelSerializer):

    faculty = FacultySerializer(required=True)

    class Meta:
        model = Lecturer
        fields = '__all__'

    # overriding the create method
    def create(self, validated_data):

        faculty = None

        faculty_data = validated_data.pop('faculty')
        serialized_faculty = FacultySerializer(data=faculty_data)

        if (serialized_faculty.is_valid()):
            # faculty, faculty_created = Faculty.objects.get_or_create(defaults={}, faculty_id=serialized_faculty.data['faculty_id'])
            faculty = Faculty.objects.filter(faculty_id=serialized_faculty.data['faculty_id'])

            if (len(faculty) == 1):
                lecturer, created = Lecturer.objects.update_or_create(
                    faculty=faculty[0],
                    lecturer_id=validated_data.pop('lecturer_id'),
                    fname=validated_data.pop('fname'),
                    lname=validated_data.pop('lname'),
                    email=validated_data.pop('email'),
                    telephone=validated_data('telephone')
                )

                return lecturer

            return None

        return None


# serializer for Lecturer_Subject
class LecturerSubjectSerializer(serializers.ModelSerializer):

    lecturer_id = LecturerSerializer()

    class Meta:
        model = LecturerSubject
        fields = '__all__'


# serializer for timetables
class FacultyTimetableSerializer(serializers.ModelSerializer):

    faculty = FacultySerializer(required=True)
    timetable = serializers.SerializerMethodField()

    def get_timetable(self, obj):
        return_data = []

        for table in obj.timetable:
            time_table = {}
            time_slots = []
            time_table["date"] = table.date

            for slot in table.time_slots:
                slot_data = {"start_time": slot.start_time, "end_time": slot.end_time,
                             "subject": SubjectSerializer(slot.subject).data,
                             "lecturer": LecturerSerializer(slot.lecturer).data, "location": slot.location}

                time_slots.append(slot_data)

            time_table["time_slots"] = time_slots

            return_data.append(time_table)

        return return_data


    class Meta:
        model = FacultyTimetable
        fields = ('timetable_id', 'faculty', 'timetable')


# lecture video serializer
class LectureVideoSerializer(serializers.ModelSerializer):

    lecturer = LecturerSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = LectureVideo
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
        last_lec_video = LectureVideo.objects.order_by('lecture_video_id').last()
        # create the next lecture video id
        new_lecture_video_id = ig.generate_new_id(last_lec_video.lecture_video_id)

        # if both subject and lecturer details are available
        if len(lecturer) == 1 & len(subject) == 1:
            str_video_length = data.get('video_length')
            video_length_parts = str_video_length.split(':')
            video_length = datetime.timedelta(minutes=int(video_length_parts[0]), seconds=int(video_length_parts[1]),
                                              milliseconds=int(video_length_parts[2]))

        # this data will be passed as validated data
        validated_data = {
            'lecture_video_id': new_lecture_video_id,
            'lecturer': lecturer_ser_data,
            'subject': subject_ser_data,
            'date': data.get('date'),
            'video_name': data.get('video_name'),
            'video_length': video_length
        }

        return super(LectureVideoSerializer, self).to_internal_value(validated_data)




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
        last_lec_video = LectureVideo.objects.order_by('lecture_video_id').last()
        # create the next lecture video id
        new_lecture_video_id = ig.generate_new_id(last_lec_video.lecture_video_id)


        # if both subject and lecturer details are available
        if len(lecturer) == 1 & len(subject) == 1:

            str_video_length = validated_data.pop('video_length')
            video_length_parts = str_video_length.split(':')
            video_length = datetime.timedelta(minutes=int(video_length_parts[0]), seconds=int(video_length_parts[1]), milliseconds=int(video_length_parts[2]))

            lecture_video, created = LectureVideo.objects.update_or_create(
                lecture_video_id=new_lecture_video_id,
                lecturer=lecturer[0],
                subject=subject[0],
                date=validated_data.pop('date'),
                video_name=validated_data.pop('video_name'),
                video_length=video_length
            )

            # retrieve the created object
            created_lecture_video = LectureVideo.objects.filter(lecture_video_id=lecture_video)
            create_lecture_video_ser = LectureVideoSerializer(created_lecture_video, many=True)
            create_lecture_video_ser_data = create_lecture_video_ser.data

        # faculty_data = validated_data.pop('faculty')
        # serialized_faculty = FacultySerializer(data=faculty_data)
        #
        # if (serialized_faculty.is_valid()):
        #     # faculty, faculty_created = Faculty.objects.get_or_create(defaults={}, faculty_id=serialized_faculty.data['faculty_id'])
        #     faculty = Faculty.objects.filter(faculty_id=serialized_faculty.data['faculty_id'])
        #
        #     if (len(faculty) == 1):
        #         lecturer, created = Lecturer.objects.update_or_create(
        #             faculty=faculty[0],
        #             lecturer_id=validated_data.pop('lecturer_id'),
        #             fname=validated_data.pop('fname'),
        #             lname=validated_data.pop('lname'),
        #             email=validated_data.pop('email'),
        #             telephone=validated_data('telephone')
        #         )
        #
        #         return lecturer
        #
            return create_lecture_video_ser_data

        return None


# lecture video time landmarks serializer
class LectureVideoTimeLandmarksSerializer(serializers.ModelSerializer):

    lecture_video_id = LectureVideoSerializer()
    time_landmarks = serializers.SerializerMethodField()

    def get_time_landmarks(self, obj):
        return_data = []

        for time_landmark in obj.time_landmarks:
            landmark_details = {}
            landmark_details["landmark"] = time_landmark.landmark

            return_data.append(landmark_details)

        return return_data


    class Meta:
        model = LectureVideoTimeLandmarks
        fields = '__all__'

# lecture video frame landmarks serializer
class LectureVideoFrameLandmarksSerializer(serializers.ModelSerializer):

    lecture_video_id = LectureVideoSerializer()
    frame_landmarks = serializers.SerializerMethodField()

    def get_frame_landmarks(self, obj):
        return_data = []

        for frame_landmark in obj.frame_landmarks:
            landmark_details = {}
            landmark_details["landmark"] = frame_landmark.landmark

            return_data.append(landmark_details)

        return return_data


    class Meta:
        model = LectureVideoFrameLandmarks
        fields = '__all__'


# Lecture activity serializer
class LectureActivitySerializer(serializers.ModelSerializer):

    lecture_video_id = LectureVideoSerializer()

    class Meta:
        model = LectureActivity
        fields = '__all__'


# Lecture Activity Frame Group Serializer
class LectureActivityFrameGroupingsSerializer(serializers.ModelSerializer):

    lecture_activity_id = LectureActivitySerializer()
    frame_group_details = serializers.SerializerMethodField()

    def get_frame_group_details(self, obj):
        return_data = []

        for frame_group in obj.frame_group_details:
            group_details = {}
            group_details["frame_group_percentages"] = {}

            group_details["frame_group"] = frame_group.frame_group
            group_details["frame_group_percentages"]["phone_perct"] = frame_group.frame_group_percentages.phone_perct
            group_details["frame_group_percentages"]["listen_perct"] = frame_group.frame_group_percentages.listen_perct
            group_details["frame_group_percentages"]["note_perct"] = frame_group.frame_group_percentages.note_perct

            return_data.append(group_details)

        return return_data

    class Meta:
        model = LectureActivityFrameGroupings
        fields = '__all__'


# lecture activity frame recognition serializer
class LectureActivityFrameRecognitionsSerializer(serializers.ModelSerializer):

    lecture_activity_id = LectureActivitySerializer()
    frame_recognition_details = serializers.SerializerMethodField()

    # this method will be used to serialize the 'frame_recogition_details' field
    def get_frame_recognition_details(self, obj):

        return_data = []

        for frame_recognition in obj.frame_recognition_details:
            recognition = {}

            recognition["frame_name"] = frame_recognition.frame_name
            recognition["phone_perct"] = frame_recognition.phone_perct
            recognition["listen_perct"] = frame_recognition.listen_perct
            recognition["note_perct"] = frame_recognition.note_perct

            return_data.append(recognition)

        # return the data
        return return_data


    class Meta:
        model = LectureActivityFrameRecognitions
        fields = '__all__'



# EMOTIONS section
# lecture emotions serailzier
class LectureEmotionSerializer(serializers.ModelSerializer):
    lecture_video_id = LectureVideoSerializer()

    class Meta:
        model = LectureEmotionReport
        fields = '__all__'


# Lecture emotion Frame Group Serializer
class LectureEmotionFrameGroupingsSerializer(serializers.ModelSerializer):

    lecture_emotion_id = LectureEmotionSerializer()
    frame_group_details = serializers.SerializerMethodField()

    def get_frame_group_details(self, obj):
        return_data = []

        for frame_group in obj.frame_group_details:
            group_details = {}
            group_details["frame_group_percentages"] = {}

            group_details["frame_group"] = frame_group.frame_group
            group_details["frame_group_percentages"]["happy_perct"] = frame_group.frame_group_percentages.happy_perct
            group_details["frame_group_percentages"]["sad_perct"] = frame_group.frame_group_percentages.sad_perct
            group_details["frame_group_percentages"]["angry_perct"] = frame_group.frame_group_percentages.angry_perct
            group_details["frame_group_percentages"]["disgust_perct"] = frame_group.frame_group_percentages.disgust_perct
            group_details["frame_group_percentages"]["surprise_perct"] = frame_group.frame_group_percentages.surprise_perct
            group_details["frame_group_percentages"]["neutral_perct"] = frame_group.frame_group_percentages.neutral_perct

            return_data.append(group_details)

        return return_data


    class Meta:
        model = LectureEmotionFrameGroupings
        fields = '__all__'



# lecture emotion frame recognition serializer
class LectureEmotionFrameRecognitionsSerializer(serializers.ModelSerializer):

    lecture_emotion_id = LectureEmotionSerializer()
    frame_recognition_details = serializers.SerializerMethodField()

    # this method will be used to serialize the 'frame_recogition_details' field
    def get_frame_recognition_details(self, obj):

        return_data = []

        for frame_recognition in obj.frame_recognition_details:
            recognition = {}

            recognition["frame_name"] = frame_recognition.frame_name
            recognition["happy_perct"] = frame_recognition.happy_perct
            recognition["sad_perct"] = frame_recognition.sad_perct
            recognition["angry_perct"] = frame_recognition.angry_perct
            recognition["surprise_perct"] = frame_recognition.surprise_perct
            recognition["neutral_perct"] = frame_recognition.neutral_perct

            return_data.append(recognition)

        # return the data
        return return_data


    class Meta:
        model = LectureEmotionFrameRecognitions
        fields = '__all__'



# lecture video meta serializer
class VideoMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoMeta
        fields = '__all__'

# lecture gaze serializer
class LectureGazeEstimationSerializer(serializers.ModelSerializer):

    lecture_video_id = LectureVideoSerializer()

    class Meta:
        model = LectureGazeEstimation
        fields = '__all__'


# Lecture emotion Frame Group Serializer
class LectureGazeFrameGroupingsSerializer(serializers.ModelSerializer):

    lecture_gaze_id = LectureGazeEstimationSerializer()
    frame_group_details = serializers.SerializerMethodField()

    def get_frame_group_details(self, obj):
        return_data = []

        for frame_group in obj.frame_group_details:
            group_details = {}
            group_details["frame_group_percentages"] = {}

            group_details["frame_group"] = frame_group.frame_group
            group_details["frame_group_percentages"]["upright_perct"] = frame_group.frame_group_percentages.upright_perct
            group_details["frame_group_percentages"]["upleft_perct"] = frame_group.frame_group_percentages.upleft_perct
            group_details["frame_group_percentages"]["downright_perct"] = frame_group.frame_group_percentages.downright_perct
            group_details["frame_group_percentages"]["downleft_perct"] = frame_group.frame_group_percentages.downleft_perct
            group_details["frame_group_percentages"]["front_perct"] = frame_group.frame_group_percentages.front_perct

            return_data.append(group_details)

        return return_data


    class Meta:
        model = LectureGazeFrameGroupings
        fields = '__all__'



# lecture emotion frame recognition serializer
class LectureGazeFrameRecognitionsSerializer(serializers.ModelSerializer):

    lecture_gaze_id = LectureGazeEstimationSerializer()
    frame_recognition_details = serializers.SerializerMethodField()

    # this method will be used to serialize the 'frame_recogition_details' field
    def get_frame_recognition_details(self, obj):

        return_data = []

        for frame_recognition in obj.frame_recognition_details:
            recognition = {}

            recognition["frame_name"] = frame_recognition.frame_name
            recognition["upright_perct"] = frame_recognition.upright_perct
            recognition["upleft_perct"] = frame_recognition.upleft_perct
            recognition["downright_perct"] = frame_recognition.downright_perct
            recognition["downleft_perct"] = frame_recognition.downleft_perct
            recognition["front_perct"] = frame_recognition.front_perct

            return_data.append(recognition)

        # return the data
        return return_data


    class Meta:
        model = LectureGazeFrameRecognitions
        fields = '__all__'