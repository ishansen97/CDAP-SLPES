from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Student, Subject, Attendance
from .serializers import StudentSerializer, SubjectSerializer, AttendanceSerializer, FileSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from . import record
from . import test as t

from rest_framework.views import *

class StudentAPIView(APIView):

    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetails(APIView):

    def get_object(self, pk):
        try:
            return Student.objects.get(studentId=pk)

        except Student.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = self.get_object(pk)
        student.delete(student)
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def student_list(request):
    if request.method == 'GET':
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GEt', 'PUT', 'DELETE'])
def student_detail(request, pk):
    try:
        student = Student.objects.get(studentId=pk)

    except Student.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        student.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def subject_list(request):
    if request.method == 'GET':
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SubjectSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def subject_detail (request, pk):
    try:
        subject = Subject.objects.get(subjectId=pk)

    except subject.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'GET':
        serializer = SubjectSerializer(subject)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SubjectSerializer(subject, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        subject.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'POST'])
def attendance_list(request):
    if request.method == 'GET':
        attendance = Attendance.objects.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AttendanceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileView(APIView):
    # parser_classes = (MultiPartParser, FormParser)

  def post(self, request, *args, **kwargs):
    file_serializer = FileSerializer(data=request.data)
    if file_serializer.is_valid():
      file_serializer.save()
      return Response(file_serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# this API will initiate the lecture
class InitiateLecture(APIView):

    def get(self, request):
        record.initiate()

        return Response({
            "response": "success"
        })

class stopRecording(APIView):
    def get(self, request):
        t.isStop = 1
        return Response({
            "response": "stopped"
        })
    def post(self, request):
        pass

# test method (delete later)
class TestAPI(APIView):

    def get(self, request):
        t.isStop = 0
        param = request.query_params.get('param')

        # t.test()
        t.IPWebcamTest()

        return Response({
            "response": "started"
        })

    def post(self, request):
        pass