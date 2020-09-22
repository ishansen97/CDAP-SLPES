from django.contrib import admin

# Register your models here.
from LectureSummarizingApp.models import *

admin.site.register(LectureAudio)
admin.site.register(LectureAudioNoiseRemoved)
admin.site.register(LectureSpeechToText)
admin.site.register(LectureAudioSummary)
