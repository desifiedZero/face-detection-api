from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status, generics
from api.serializers import EntrySerializer, ProjectActivitySerializer, UserRegistrationSerializer, UserSerializer, GroupSerializer, ProjectSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework import status
from api.models import Entry, Project, ProjectActivity
from django.shortcuts import get_object_or_404

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class Auth(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                return Response({
                        "user": UserSerializer(
                            user, context=self.get_serializer_context()
                        ).data,
                        "message": "User Created Successfully.",
                    })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            # print error to console for debugging do not raise
            print("Error: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            # attach user to project 
            user = User.objects.get(id=self.request.user.id)
            project = Project.objects.get(id=serializer.data['id'])
            project.users.add(user)
            project.save()

            return Response(
                {"message": "Project created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProjectsView(APIView):
    def get(self, request, *args, **kwargs):
        items = Project.objects.filter(users__id=self.request.user.id)
        serializer = ProjectSerializer(items, many=True)
        return Response(serializer.data, *args, **kwargs)
    
class ActivityView(APIView):    
    def get(self, request, *args, **kwargs):
        items = ProjectActivity.objects.filter(project__users__id=self.request.user.id)
        serializer = ProjectActivitySerializer(items, many=True)
        return Response(serializer.data, *args, **kwargs)

class EntryView(APIView):
    # create an api for multipart form data
    def post(self, request, *args, **kwargs):
        serializer = EntrySerializer(data=request.data, context={'request': request})        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Entry created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, project_id, *args, **kwargs):
        items = Entry.objects.filter(project__id=project_id)
        serializer = EntrySerializer(items, many=True)
        return Response(serializer.data, *args, **kwargs)
    
class ActivityView(APIView):
    def get(self, request, project_id, *args, **kwargs):
        activity = ProjectActivity.objects.filter(project__id=project_id).order_by('-created_at')

        # get activity from database and serialize
        serializer = ProjectActivitySerializer(activity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)