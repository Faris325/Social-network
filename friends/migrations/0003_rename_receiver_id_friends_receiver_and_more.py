# Generated by Django 4.2.20 on 2025-04-19 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0002_alter_friends_application_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friends',
            old_name='receiver_id',
            new_name='receiver',
        ),
        migrations.RenameField(
            model_name='friends',
            old_name='sender_id',
            new_name='sender',
        ),
    ]
