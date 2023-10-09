from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status, generics
from api.serializers import EntrySerializer, ProjectActivitySerializer, UserRegistrationSerializer, UserSerializer, GroupSerializer, ProjectSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework import status, mixins
from api.models import Entry, Project, ProjectActivity, ProjectInviteToken, ProjectUserRelationship
from .permissions import (
    InvitePermission
)
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from .face_detector import (
    train,
    test_face_recognitions
)
from django.conf import settings
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
import os 

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
        activity = ProjectActivity.objects.filter(
            project__id=project_id
        ).order_by('-created_at')
        serializer = ProjectActivitySerializer(activity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InviteView(APIView):
    permission_classes = [InvitePermission]

    def post(self, request, project_id):
        user_email = request.data.get("email")

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = Project.objects.get(id = project_id)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

        token = default_token_generator.make_token(user)
        token = urlsafe_base64_encode(force_bytes(token))

        _token = ProjectInviteToken.objects.create(
            user=user, token=token, project=project
        )

        # Send the email
        accept_link = f"{request.get_host()}/api/invite/accept/{project_id}/{token}/"
        decline_link = f"{request.get_host()}/api/invite/decline/{project_id}/{token}/"
        message = render_to_string('invite.html', {'accept_link': accept_link, 'decline_link': decline_link})
        email = EmailMessage("Project Invite", message, to=[user.email])
        email.send()

        return Response({"detail": "Invite sent to the email"}, status=status.HTTP_200_OK)


class InviteAcceptView(APIView):

      def get(self, request, project_id, token):
        try:
            invite_obj = ProjectInviteToken.objects.get(token=token)
        except ProjectInviteToken.DoesNotExist:
            return Response({"detail": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)

        user = invite_obj.user
        try:
            project = Project.objects.get(
                id = project_id
            )
        except Project.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        proj = ProjectUserRelationship.objects.create(
            user = user,
            project = project,
        )
        invite_obj.delete()
        return Response({"detail": "Added to project successful"}, status=status.HTTP_200_OK)
      

class InviteDeclineView(APIView):

      def get(self, request, project_id, token):
        try:
            invite_obj = ProjectInviteToken.objects.get(token=token)
        except ProjectInviteToken.DoesNotExist:
            return Response({"detail": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)

        invite_obj.delete()
        return Response({"detail": "Successfully declined"}, status=status.HTTP_200_OK)


class FileUploadView(APIView):
    
    # permission_classes = [permissions.IsAuthenticated]

     def post(self, request):
        project_id = request.data.get('project_id')
        base_image_folder = os.path.join(settings.BASE_DIR, 'images', 'images')
        folder = os.path.join(base_image_folder, str(project_id))

        model = train(folder)

        uploaded_images = request.FILES
        print(uploaded_images)
        recognized = test_face_recognitions(uploaded_images, folder, model)

        return Response(recognized, content_type='image/jpeg')

    # def post(self, request):
    #     folder = f"images/images/{request.data.get('project_id')}/"
    #     print(folder)
    #     model = train(folder)
    #     image = [i for i in self.request.FILES]
    #     print(image)
    #     recognized = test_face_recognitions(image, folder, model)
    #     return Response(recognized, content_type='image/jpeg')