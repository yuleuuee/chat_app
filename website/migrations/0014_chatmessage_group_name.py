# Generated by Django 5.0.2 on 2024-03-15 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_chatmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='group_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
