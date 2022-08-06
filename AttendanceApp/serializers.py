from rest_framework import serializers

from FirstApp.serializers import SubjectSerializer
from .models import Student, Subject, Attendance, File, TrainingData


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingData
        fields = '__all__'

#
# class SubjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subject
#         fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):

    subject = SubjectSerializer()

    class Meta:
        model = Attendance
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta():
        model = File
        fields = ('file', 'remark', 'timestamp')
