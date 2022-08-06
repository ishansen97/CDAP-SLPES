# Generated by Django 2.2.12 on 2020-09-22 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0001_initial'),
        ('LectureSummarizingApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LectureAudioNoiseRemoved',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecture_audio_id', models.CharField(max_length=10)),
                ('lecturer_date', models.DateField()),
                ('lecture_audio_name', models.CharField(max_length=50)),
                ('lecture_audio_length', models.DurationField()),
                ('lecturer', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='FirstApp.Lecturer')),
                ('subject', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='FirstApp.Subject')),
            ],
        ),
    ]
