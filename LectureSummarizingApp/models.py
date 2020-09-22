# from django.db import models
from djongo import models

# Create your models here.
from FirstApp.MongoModels import Lecturer, Subject


class LectureAudio (models.Model):
    lecture_audio_id = models.CharField(max_length=10)
    lecturer_date = models.DateField()
    lecture_audio_name = models.CharField(max_length=50)
    lecture_audio_length = models.DurationField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, default=0)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.lecture_audio_id

class LectureAudioSummary (models.Model):
    lecture_audio_summary_id = models.CharField(max_length=10)
    lecture_audio_id = models.ForeignKey(LectureAudio, on_delete=models.CASCADE)
    audio_original_text = models.TextField()
    audio_summary = models.TextField()

    def __str__(self):
        return self.lecture_audio_summary_id
