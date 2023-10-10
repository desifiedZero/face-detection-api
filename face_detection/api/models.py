from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Project(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    storageSchema = models.JSONField(null=True)
    users = models.ManyToManyField(User, through='ProjectUserRelationship', related_name='projects')

    @property
    def registered(self):
        return self.users.count()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)
    
class ProjectUserRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'project']


def resolve_pathname(instance, filename):
    project_id = instance.project.id if instance.project else None
    upload_to = f'images/{project_id}/{filename}'
    return upload_to

class Entry(models.Model):
    entry_id = models.AutoField(primary_key=True)
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
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="entries")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.entry_detail_id)
    
class EntryImage(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=resolve_pathname)
    
class ProjectActivity(models.Model):
    project_activity_id = models.AutoField(primary_key=True)
    activity_type = models.CharField(max_length=100)
    activity_data = models.JSONField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.project_activity_id)

class ProjectInviteToken(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    token = models.CharField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name + self.project.name