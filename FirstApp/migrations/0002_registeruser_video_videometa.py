# Generated by Django 2.2.11 on 2020-03-16 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisterUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=20)),
                ('lastName', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('path', models.CharField(max_length=100)),
                ('duration', models.CharField(max_length=100)),
                ('hours', models.IntegerField()),
                ('minutes', models.IntegerField()),
                ('seconds', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='VideoMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fps', models.IntegerField()),
                ('frame_count', models.IntegerField()),
                ('happy_count', models.IntegerField()),
                ('sad_count', models.IntegerField()),
                ('angry_count', models.IntegerField()),
                ('neutral_count', models.IntegerField()),
                ('surprise_count', models.IntegerField()),
                ('happy_perct', models.IntegerField()),
                ('sad_perct', models.IntegerField()),
                ('angry_perct', models.IntegerField()),
                ('neutral_perct', models.IntegerField()),
                ('surprise_perct', models.IntegerField()),
            ],
        ),
    ]
