# Generated by Django 4.2.5 on 2023-10-09 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='storageSchema',
            field=models.JSONField(null=True),
        ),
    ]
