from django.contrib import admin

from api.models import (
    Entry, 
    EntryDetails, 
    Project, 
    ProjectUserRelationship, 
    ProjectActivity,
    EntryImage,
    ProjectInviteToken
)

# Register your models here.
admin.site.site_header = "Face Detection Admin"
admin.site.site_title = "Face Detection Admin Portal"
admin.site.index_title = "Welcome to Face Detection Portal"

# register Entry and ExtryDetails
admin.site.register(Entry)
admin.site.register(EntryDetails)
admin.site.register(ProjectActivity)
admin.site.register(EntryImage)
admin.site.register(ProjectInviteToken)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ('users',)

@admin.register(ProjectUserRelationship)
class ProjectUserRelationshipAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'added_date']
    list_filter = ['user', 'project', 'added_date']
