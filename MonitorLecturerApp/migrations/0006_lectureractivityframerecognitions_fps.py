# Generated by Django 2.2.11 on 2020-10-25 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MonitorLecturerApp', '0005_lectureractivityframerecognitions'),
    ]

    operations = [
        migrations.AddField(
            model_name='lectureractivityframerecognitions',
            name='fps',
            field=models.FloatField(default=30.0),
        ),
    ]
