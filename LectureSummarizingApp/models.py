from djongo import models

# Models used in Lecture Summarization Component
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


class LectureAudioNoiseRemoved (models.Model):
    lecture_audio_noise_removed_id = models.CharField(max_length=10)
    lecture_audio_id = models.ForeignKey(LectureAudio, on_delete=models.CASCADE, default=0)
    lecturer_date = models.DateField()
    lecture_audio_name = models.CharField(max_length=50)
    lecture_audio_length = models.DurationField()

    def __str__(self):
        return self.lecture_audio_noise_removed_id


class LectureSpeechToText (models.Model):
    lecture_speech_to_text_id = models.CharField(max_length=10)
    lecture_audio_id = models.ForeignKey(LectureAudio, on_delete=models.CASCADE)
    audio_original_text = models.TextField()

    def __str__(self):
        return self.lecture_speech_to_text_id


class LectureAudioSummary (models.Model):
    lecture_audio_summary_id = models.CharField(max_length=10)
    lecture_audio_id = models.ForeignKey(LectureAudio, on_delete=models.CASCADE)
    audio_original_text = models.TextField()
    audio_summary = models.TextField()

    def __str__(self):
        return self.lecture_audio_summary_id


class LectureNotices (models.Model):
    lecture_notice_id = models.CharField(max_length=10)
    lecture_audio_id = models.ForeignKey(LectureAudio, on_delete=models.CASCADE)
    notice_text = models.TextField()

    def __str__(self):
        return self.lecture_notice_id

