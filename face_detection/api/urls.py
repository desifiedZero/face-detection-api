from django.urls import include, path
from rest_framework import routers
from api import views
from rest_framework.authtoken.views import obtain_auth_token
from .views import CreateProject, GetProject
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('create_project/', csrf_exempt(CreateProject.as_view()), name='create_project'),
    path('get_projects/', csrf_exempt(GetProject.as_view()), name='get_projects'),
    path('api/token/', views.Auth.as_view(), name='login'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
