# Generated by Django 2.2.12 on 2020-09-23 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('FirstApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('remark', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('studentId', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('studentFirstName', models.CharField(max_length=100)),
                ('studentLastName', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('year', models.CharField(max_length=100)),
                ('semester', models.CharField(max_length=100)),
                ('batch', models.CharField(max_length=100)),
                ('faculty', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('lectureID', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('startTime', models.DateField()),
                ('endTime', models.DateField()),
                ('day', models.CharField(max_length=20)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FirstApp.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('attendanceID', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('attendance', models.BooleanField()),
                ('feedback', models.CharField(blank=True, max_length=50, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AttendanceApp.Student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FirstApp.Subject')),
            ],
        ),
    ]
