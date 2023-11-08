from django.urls import include, path
from rest_framework import routers
from . import views
from .views import ActivityView, ProjectView, ProjectsView, EntryView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/project/', csrf_exempt(ProjectView.as_view()), name='project'),
    path('api/project/<int:project_id>/', csrf_exempt(ProjectView.as_view()), name='get_project'),
    path('api/project/<int:project_id>/activity/', csrf_exempt(ActivityView.as_view()), name='get_activity'),
    path('api/project/<int:project_id>/entries/', EntryView.as_view(), name='entries'),
    
    path('api/projects/', ProjectsView.as_view(), name='get_projects'),

    path('api/token/', views.Auth.as_view(), name='login'),
    path('api/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/me/', views.ActiveUserView.as_view(), name='user'),

    path('api/invite/', views.InviteView.as_view(), name="invite"),
    path('api/invite/list/', views.ListInvitesView.as_view(), name="list-invite"),
    path('api/project/<int:project_id>/invite/', views.InviteView.as_view(), name="invite"),

    path('api/invite/accept/<int:project_id>/<str:token>/', views.InviteAcceptView.as_view(), name="accept-invite"),
    path('api/invite/decline/<int:project_id>/<str:token>/', views.InviteDeclineView.as_view(), name="decline-invite"),
    
    path('api/face/register/', views.FaceRegisterView.as_view(), name="face-register"),
    path('api/project/<int:project_id>/face/register/<int:entry_id>/', views.FaceRegisterView.as_view(), name="face-register"),
    path('api/face/scan/', views.FaceScanView.as_view(), name="face-scan"),

    path('api/project/<int:project_id>/adminpermission/<int:user_id>/', views.AdminPermissionView.as_view(), name="admin-permission"),
    path('api/project/<int:project_id>/associate/', views.ProjectUserView.as_view(), name="project-user-relationship"),
    path('api/project/<int:project_id>/user/', views.AdminPermissionView.as_view(), name="admin-permission"),
    path('api/project/<int:project_id>/manage/users/', views.ProjectUserManagerView.as_view(), name="admin-permission"),
    path('api/project/<int:project_id>/manage/users/<int:user_id>/', views.ProjectUserManagerView.as_view(), name="admin-permission"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
