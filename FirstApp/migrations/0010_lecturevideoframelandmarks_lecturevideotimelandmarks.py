# Generated by Django 2.2.11 on 2020-10-09 09:10

import FirstApp.MongoModels
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0009_lectureactivityframegroupings'),
    ]

    operations = [
        migrations.CreateModel(
            name='LectureVideoTimeLandmarks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecture_video_time_landmarks_id', models.CharField(max_length=15)),
                ('time_landmarks', djongo.models.fields.ArrayField(model_container=FirstApp.MongoModels.Landmarks)),
                ('lecture_video_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FirstApp.LectureVideo')),
            ],
        ),
        migrations.CreateModel(
            name='LectureVideoFrameLandmarks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecture_video_frame_landmarks_id', models.CharField(max_length=15)),
                ('frame_landmarks', djongo.models.fields.ArrayField(model_container=FirstApp.MongoModels.Landmarks)),
                ('lecture_video_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FirstApp.LectureVideo')),
            ],
        ),
    ]
