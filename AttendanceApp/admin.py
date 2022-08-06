from django.contrib import admin
from .models import Student, Attendance, TrainingData

admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(TrainingData)

# Register your models here.
