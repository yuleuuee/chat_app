# Generated by Django 5.0.2 on 2024-02-29 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0011_otpmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='no_of_comments',
            field=models.IntegerField(default=0),
        ),
    ]
