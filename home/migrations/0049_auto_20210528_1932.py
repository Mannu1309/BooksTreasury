# Generated by Django 3.2.3 on 2021-05-28 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0048_auto_20210528_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='books',
            name='slug',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cathome',
            name='slug',
            field=models.SlugField(max_length=255, null=True),
        ),
    ]
