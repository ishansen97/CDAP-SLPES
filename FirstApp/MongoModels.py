from djongo import models
from datetime import datetime

# Lecture model
class Lecture(models.Model):
    lecture_id = models.CharField(max_length=10)
    date = models.DateTimeField(auto_created=True, default=None)



# Faculty model
class Faculty(models.Model):
    faculty_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.faculty_id

# Subjects model
class Subject(models.Model):
    subject_code = models.TextField()
    name = models.TextField()
    year = models.IntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, default={})

    def __str__(self):
        return self.subject_code


# Lecturer model
class Lecturer(models.Model):
    lecturer_id = models.CharField(max_length=7)
    fname = models.TextField()
    lname = models.TextField()
    email = models.EmailField()
    telephone = models.CharField(max_length=10)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.lecturer_id


# Lecturer_subject model
class LecturerSubject(models.Model):
    lec_subject_id = models.CharField(max_length=10)
    lecturer_id = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(to=Subject)

    def __str__(self):
        return self.lec_subject_id


# lecturer credential details
class LecturerCredentials(models.Model):
    username = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    password = models.CharField(max_length=15)


# timetable based on daily basis
class DailyTimeTable(models.Model):
    slot_id = models.AutoField(auto_created=True, primary_key=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    location = models.CharField(max_length=10)

    def __str__(self):
        return self.location

    class Meta:
        abstract = True


# Timetable based on day basis
class DateTimeTable(models.Model):
    date = models.DateField()
    time_slots = models.ArrayField(
        model_container=DailyTimeTable
    )

    def __bool__(self):
        return True if self.date is not None else False

    class Meta:
        abstract = True


# faculty timetable
class FacultyTimetable(models.Model):
    timetable_id = models.CharField(max_length=10)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    timetable = models.ArrayField(DateTimeTable)

    def __str__(self):
        return self.timetable_id


# lecture video table
class LectureVideo(models.Model):
    lecture_video_id = models.CharField(max_length=10)
    date = models.DateField()
    video_name = models.CharField(max_length=50)
    video_length = models.DurationField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, default=0)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=0)

    models.UniqueConstraint(fields=[date], name='date_unique')

    def __str__(self):
        return self.lecture_video_id



class Landmarks(models.Model):
    landmark = models.CharField(max_length=15)

    class Meta:
        abstract = True


# lecture video time landmarks table
class LectureVideoTimeLandmarks(models.Model):
    lecture_video_time_landmarks_id = models.CharField(max_length=15)
    lecture_video_id = models.ForeignKey(LectureVideo, on_delete=models.CASCADE)
    time_landmarks = models.ArrayField(Landmarks)

    def __str__(self):
        return self.lecture_video_time_landmarks_id


# lecture video frame landmarks table
class LectureVideoFrameLandmarks(models.Model):
    lecture_video_frame_landmarks_id = models.CharField(max_length=15)
    lecture_video_id = models.ForeignKey(LectureVideo, on_delete=models.CASCADE)
    frame_landmarks = models.ArrayField(Landmarks)

    def __str__(self):
        return self.lecture_video_frame_landmarks_id



# ACTIVITY section
# lecture activity table
class LectureActivity(models.Model):
    lecture_activity_id = models.CharField(max_length=10)
    lecture_video_id = models.ForeignKey(LectureVideo, on_delete=models.CASCADE)
    talking_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    listening_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    writing_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    phone_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    def __str__(self):
        return self.lecture_activity_id


# this abstract class will define the lecture activity frame group percentages
class LectureActivityFrameGroupPercentages(models.Model):
    phone_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    listen_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    note_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    class Meta:
        abstract = True


# this abstract class will define the details for an activity frame group
class LectureActivityFrameGroupDetails(models.Model):
    frame_group = models.CharField(max_length=10)
    frame_group_percentages = models.EmbeddedField(
       model_container=LectureActivityFrameGroupPercentages
    )

    class Meta:
        abstract = True


# this class will contain the activity frame groupings
class LectureActivityFrameGroupings(models.Model):
    lecture_activity_frame_groupings_id = models.CharField(max_length=15, default="")
    lecture_activity_id = models.ForeignKey(LectureActivity, on_delete=models.CASCADE)
    frame_group_details = models.ArrayField(model_container=LectureActivityFrameGroupDetails)

    def __str__(self):
        return self.lecture_activity_frame_groupings_id



# this abstract class will contain lecture activity frame recognition details
class LectureActivityFrameRecognitionDetails(models.Model):
    frame_name = models.CharField(max_length=15)
    phone_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    listen_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    note_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    class Meta:
        abstract = True


# this class will contain lecture activity frame recognitions
class LectureActivityFrameRecognitions(models.Model):
    lecture_activity_frame_recognition_id = models.CharField(max_length=15)
    lecture_activity_id = models.ForeignKey(LectureActivity, on_delete=models.CASCADE)
    frame_recognition_details = models.ArrayField(LectureActivityFrameRecognitionDetails)

    def __str__(self):
        return self.lecture_activity_frame_recognition_id



# EMOTIONS section
# Lecture emotion report
class LectureEmotionReport(models.Model):
    lecture_emotion_id = models.CharField(max_length=10)
    lecture_video_id = models.ForeignKey(LectureVideo, on_delete=models.CASCADE, default=0)
    happy_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    sad_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    angry_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    disgust_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    surprise_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    neutral_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)


    def __str__(self):
        return self.lecture_emotion_id


# this abstract class will define the lecture emotion frame group percentages
class LectureEmotionFrameGroupPercentages(models.Model):
    happy_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    sad_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    angry_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    disgust_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    surprise_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    neutral_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    class Meta:
        abstract = True


# this abstract class will define the details for an emotion frame group
class LectureEmotionFrameGroupDetails(models.Model):
    frame_group = models.CharField(max_length=10)
    frame_group_percentages = models.EmbeddedField(
       model_container=LectureEmotionFrameGroupPercentages
    )

    class Meta:
        abstract = True


# this class will contain the emotion frame groupings
class LectureEmotionFrameGroupings(models.Model):
    lecture_emotion_frame_groupings_id = models.CharField(max_length=15, default="")
    lecture_emotion_id = models.ForeignKey(LectureEmotionReport, on_delete=models.CASCADE)
    frame_group_details = models.ArrayField(model_container=LectureEmotionFrameGroupDetails)

    def __str__(self):
        return self.lecture_emotion_frame_groupings_id


# POSE section
# lecture pose estimation
class LectureGazeEstimation(models.Model):
    lecture_gaze_id = models.CharField(max_length=10)
    lecture_video_id = models.ForeignKey(LectureVideo, on_delete=models.CASCADE)
    looking_up_and_right_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    looking_up_and_left_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    looking_down_and_right_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    looking_down_and_left_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    looking_front_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    def __str__(self):
        return self.lecture_gaze_id


# this abstract class will define the lecture gaze frame group percentages
class LectureGazeFrameGroupPercentages(models.Model):
    upright_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    upleft_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    downright_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    downleft_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    front_perct = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    class Meta:
        abstract = True


# this abstract class will define the details for a gaze frame group
class LectureGazeFrameGroupDetails(models.Model):
    frame_group = models.CharField(max_length=10)
    frame_group_percentages = models.EmbeddedField(
       model_container=LectureGazeFrameGroupPercentages
    )

    class Meta:
        abstract = True


# this class will contain the gaze frame groupings
class LectureGazeFrameGroupings(models.Model):
    lecture_gaze_frame_groupings_id = models.CharField(max_length=15, default="")
    lecture_gaze_id = models.ForeignKey(LectureGazeEstimation, on_delete=models.CASCADE)
    frame_group_details = models.ArrayField(model_container=LectureGazeFrameGroupDetails)

    def __str__(self):
        return self.lecture_gaze_frame_groupings_id
