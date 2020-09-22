from django.db import models
from djongo import models

# Create your models here.
from FirstApp.MongoModels import Subject, Lecturer
from LectureSummarizingApp.models import LectureAudioSummary


class RegisterTeacher(models.Model):
    fName = models.CharField(max_length = 15)
    lName = models.CharField(max_length = 15)
    subject = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
    password = models.CharField(max_length = 50)

    def _str_(self):
        return self.fName


class LecturerVideo(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    hours = models.IntegerField()
    minutes = models.IntegerField()
    seconds = models.IntegerField()

    def __str__(self):
        return self.name


class LecturerVideoMetaData(models.Model):
    fps = models.IntegerField()
    frame_count = models.IntegerField()
    seated_count = models.IntegerField()
    standing_count = models.IntegerField()
    walking_count = models.IntegerField()

    def __int__(self):
        return self.frame_count

    def calSeatedPercent(self):
        self.seated_percent = int((self.seated_count / self.frame_count) * 100)

    def calStandPercent(self):
        self.stand_percent = int((self.standing_count / self.frame_count) * 100)

    def calWalkPercent(self):
        self.walk_percent = int((self.walking_count / self.frame_count) * 100)

    def calPercentage(self):
        self.calSeatedPercent()
        self.calStandPercent()
        self.calWalkPercent()


class LecturerAudioText (models.Model):
    lecturer_audio_text_id = models.CharField(max_length=10)
    lecturer_audio_text_wordcount = models.IntegerField()
    lecturer_audio_text_lexical_wordcount = models.IntegerField()
    lecturer_audio_text_non_lexical_wordcount = models.IntegerField()
    lecturer_audio_text_status = models.CharField(
        max_length=15,
        choices=(
            ("Below", "Below"),
            ("Average", "Average"),
            ("Excellent", "Excellent")
        ),
        default="Average"
    )
    lecturer_audio_original_text = models.ForeignKey(LectureAudioSummary, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.lecturer_audio_text_id

class LectureRecordedVideo (models.Model):
    lecture_video_id = models.CharField(max_length=10)
    lecturer_date = models.DateField()
    lecture_video_name = models.CharField(max_length=50)
    lecture_video_length = models.DurationField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, default=0)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.lecture_video_id