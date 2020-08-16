from rest_framework import serializers
from .models import RegisterTeacher, tVideoMetaData

class RegisterTeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegisterTeacher
        fields = {'fName', 'lName', 'subject', 'email', 'password'}


