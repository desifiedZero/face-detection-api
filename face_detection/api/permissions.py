from rest_framework.permissions import BasePermission
from .models import (
    ProjectUserRelationship
)

class InvitePermission(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user is an admin for the specific project
            project_id = view.kwargs.get('project_id')  # Assuming project_id is a URL parameter
            if project_id:
                try:
                    project_user_relationship = ProjectUserRelationship.objects.get(
                        user=request.user,
                        project_id=project_id
                    )
                    return project_user_relationship.is_admin
                except ProjectUserRelationship.DoesNotExist:
                    return False  # User is not associated with the project
        return False