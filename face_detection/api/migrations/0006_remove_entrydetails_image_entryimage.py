# Generated by Django 4.2.5 on 2023-10-10 16:47

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_entrydetails_entry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entrydetails',
            name='image',
        ),
        migrations.CreateModel(
            name='EntryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=api.models.resolve_pathname)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entry', to='api.entry')),
            ],
        ),
    ]