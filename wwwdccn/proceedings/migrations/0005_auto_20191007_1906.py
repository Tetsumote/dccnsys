# Generated by Django 2.2.4 on 2019-10-07 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proceedings', '0004_create_artifacts_for_existing_attachments'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cameraready',
            options={'ordering': ['id']},
        ),
    ]