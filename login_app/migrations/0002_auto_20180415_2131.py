# Generated by Django 2.0.3 on 2018-04-15 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofilemodel',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfileModel',
        ),
    ]