# from django.db import models
from djongo import models

from FirstApp.MongoModels import Subject


class Student(models.Model):
    studentId = models.CharField(primary_key=True, max_length=10)
    studentFirstName = models.CharField(max_length=100)
    studentLastName = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    semester = models.CharField(max_length=100)
    batch = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)

    def __str__(self):
        return self.studentId


# class Subject(models.Model):
#     subjectId = models.CharField(primary_key=True, max_length=10)
#     subjectName = models.CharField(max_length=100)
#     LecturerInCharge = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.subjectId


class Attendance(models.Model):
    attendanceID = models.CharField(primary_key=True, max_length=10)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    attendance = models.BooleanField()
    feedback = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.attendanceID

class File(models.Model):
  file = models.FileField(blank=False, null=False)
  remark = models.CharField(max_length=20)
  timestamp = models.DateTimeField(auto_now_add=True)


class Lecture(models.Model):
    lectureID = models.CharField(primary_key=True, max_length=10)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    startTime = models.DateField()
    endTime = models.DateField()
    day = models.CharField(max_length=20)


class TrainingData(models.Model):
    studentId = models.CharField(max_length=20, default='')
    image_1 = models.CharField(max_length=2000000, null=True, blank=True, default='')
    image_2 = models.CharField(max_length=2000000, null=True, blank=True, default='')
    image_3 = models.CharField(max_length=2000000, null=True, blank=True, default='')
    image_4 = models.CharField(max_length=2000000, null=True, blank=True, default='')
    image_5 = models.CharField(max_length=2000000, null=True, blank=True, default='')

    def __str__(self):
        return self.studentId

from django.db import models

# Create your models here.
