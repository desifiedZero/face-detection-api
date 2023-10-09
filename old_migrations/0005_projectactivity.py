# Generated by Django 4.2.5 on 2023-10-08 18:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_project_project_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectActivity',
            fields=[
                ('project_activity_id', models.AutoField(primary_key=True, serialize=False)),
                ('activity_type', models.CharField(max_length=100)),
                ('activity_data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project')),
            ],
        ),
    ]