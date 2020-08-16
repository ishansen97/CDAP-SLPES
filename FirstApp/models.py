from django.db import models

class Teachers(models.Model):
    firstName = models.CharField(max_length=10)
    lastName = models.CharField(max_length=15)
    age = models.IntegerField()

    def __str__(self):
        return self.firstName


class Video(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    hours = models.IntegerField()
    minutes = models.IntegerField()
    seconds = models.IntegerField()

    def __str__(self):
        return self.name


class VideoMeta(models.Model):
    fps = models.IntegerField()
    frame_count = models.IntegerField()
    happy_count = models.IntegerField()
    sad_count = models.IntegerField()
    angry_count = models.IntegerField()
    neutral_count = models.IntegerField()
    surprise_count = models.IntegerField()
    happy_perct = models.IntegerField()
    sad_perct = models.IntegerField()
    angry_perct = models.IntegerField()
    neutral_perct = models.IntegerField()
    surprise_perct = models.IntegerField()

    def __int__(self):
        return self.frame_count

    def calcHappyPerct(self):
        self.happy_perct = int((self.happy_count / self.frame_count) * 100)

    def calcSadPerct(self):
        self.sad_perct = int((self.sad_count / self.frame_count) * 100)

    def calcAngryPerct(self):
        self.angry_perct = int((self.angry_count / self.frame_count) * 100)

    def calcNeutralPerct(self):
        self.neutral_perct = int((self.neutral_count / self.frame_count) * 100)

    def calcSurprisePerct(self):
        self.surprise_perct = int((self.surprise_count / self.frame_count) * 100)

    def calcPercentages(self):
        self.calcHappyPerct()
        self.calcAngryPerct()
        self.calcSadPerct()
        self.calcNeutralPerct()
        self.calcSurprisePerct()


class RegisterUser(models.Model):
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.firstName


