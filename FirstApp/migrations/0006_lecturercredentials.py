# Generated by Django 2.2.11 on 2020-05-13 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0005_auto_20200513_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='LecturerCredentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=15)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FirstApp.Lecturer')),
            ],
        ),
    ]
