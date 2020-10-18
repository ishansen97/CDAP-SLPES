# Generated by Django 2.2.12 on 2020-09-23 04:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LectureSummarizingApp', '0003_auto_20200923_0002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lectureaudionoiseremoved',
            name='lecturer',
        ),
        migrations.RemoveField(
            model_name='lectureaudionoiseremoved',
            name='subject',
        ),
        migrations.AddField(
            model_name='lectureaudionoiseremoved',
            name='lecture_audio_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='LectureSummarizingApp.LectureAudio'),
        ),
        migrations.CreateModel(
            name='LectureSpeechToText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecture_speech_to_text_id', models.CharField(max_length=10)),
                ('audio_original_text', models.TextField()),
                ('lecture_audio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LectureSummarizingApp.LectureAudio')),
            ],
        ),
        migrations.CreateModel(
            name='LectureNotices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecture_notice_id', models.CharField(max_length=10)),
                ('notice_text', models.TextField()),
                ('lecture_audio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LectureSummarizingApp.LectureAudio')),
            ],
        ),
    ]
