from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(LecturerVideo)
admin.site.register(LecturerAudioText)
admin.site.register(LecturerVideoMetaData)
admin.site.register(LectureRecordedVideo)