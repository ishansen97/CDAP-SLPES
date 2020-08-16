from django.db import models
from djongo import models

# Create your models here.

class RegisterTeacher(models.Model):
    fName = models.CharField(max_length = 15)
    lName = models.CharField(max_length = 15)
    subject = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
    password = models.CharField(max_length = 50)

    def _str_(self):
        return self.fName


class tVideo(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    hours = models.IntegerField()
    minutes = models.IntegerField()
    seconds = models.IntegerField()

    def __str__(self):
        return self.name


class tVideoMetaData(models.Model):
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


class lectureAudio (models.Model):
    lecture_audio_id = models.CharField(max_length=10)
    lecturer_date = models.DateField()
    lecture_audio_name = models.CharField(max_length=50)
    lecture_audio_length = models.DurationField()
    # lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, default=0)
    # subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=0)

class lectureRecordedVideo (models.Model):
    lecture_video_id = models.CharField(max_length=10)
    lecturer_date = models.DateField()
    lecture_video_name = models.CharField(max_length=50)
    lecture_video_length = models.DurationField()
    # lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, default=0)
    # subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=0)