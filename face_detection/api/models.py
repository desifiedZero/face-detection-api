from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Project(models.Model):
    project_id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    storageSchema = models.CharField(max_length=2500)
    users = models.ManyToManyField(User, through='ProjectUserRelationship', related_name='projects')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.project_id)
    
class ProjectUserRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'project']

class Entry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/')
    optimized_image = models.JSONField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.entry_id)
    
class EntryDetails(models.Model):
    entry_detail_id = models.AutoField(primary_key=True)
    kv_key = models.CharField(max_length=100)
    kv_value = models.CharField(max_length=100)
    kv_type = models.CharField(max_length=30)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.entry_detail_id)
