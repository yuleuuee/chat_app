# Generated by Django 5.0.2 on 2024-02-23 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_alter_post_content_alter_userprofile_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='dummy.png', null=True, upload_to='profile_pics/'),
        ),
    ]