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
    path('api/projects/', ProjectsView.as_view(), name='get_projects'),
    path('api/project/<int:project_id>/entries/', EntryView.as_view(), name='entries'),

    path('api/token/', views.Auth.as_view(), name='login'),
    path('api/register/', views.UserRegistrationView.as_view(), name='register'),

    path('api/invite/generate/<int:project_id>/', views.InviteView.as_view(), name="invite"),
    path('api/invite/accept/<int:project_id>/<str:token>/', views.InviteAcceptView.as_view(), name="accept-invite"),
    path('api/invite/decline/<int:project_id>/<str:token>/', views.InviteDeclineView.as_view(), name="decline-invite"),
    path('api/recognized/', views.FileUploadView.as_view(), name="recognized"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
