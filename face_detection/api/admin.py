from django.contrib import admin

from api.models import Project, ProjectUserRelationship

# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ('users',)

@admin.register(ProjectUserRelationship)
class ProjectUserRelationshipAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'added_date']
    list_filter = ['user', 'project', 'added_date']
