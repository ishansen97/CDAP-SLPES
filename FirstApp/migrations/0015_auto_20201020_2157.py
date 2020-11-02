# Generated by Django 2.2.11 on 2020-10-20 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0014_lecturegazeframerecognitions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_id', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='AdminCredentialDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=15)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FirstApp.Admin')),
            ],
        ),
        migrations.DeleteModel(
            name='LecturePoseEstimation',
        ),
    ]
