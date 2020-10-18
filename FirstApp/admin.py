from django.contrib import admin
from .MongoModels import *
from . models import Teachers, RegisterUser

# registering the lecture emotions model
admin.site.register(LectureEmotionReport)
admin.site.register(Lecturer)
admin.site.register(Faculty)
admin.site.register(Subject)
admin.site.register(LecturerSubject)
admin.site.register(LecturerCredentials)
admin.site.register(FacultyTimetable)
admin.site.register(LectureVideo)
admin.site.register(LectureActivity)
admin.site.register(LectureGazeEstimation)