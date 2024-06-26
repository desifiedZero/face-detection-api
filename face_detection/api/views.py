from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status, generics
from api.serializers import ProjectUserRelationshipSerializer, EntrySerializer, ProjectActivitySerializer, ProjectInviteTokenSerializer, UserRegistrationSerializer, UserSerializer, GroupSerializer, ProjectSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework import status, mixins
from rest_framework.decorators import permission_classes
from api.models import Entry, EntryImage, Project, ProjectActivity, ProjectInviteToken, ProjectUserRelationship, EntryDetails
from .permissions import (
    IsProjectAdmin
)
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from .detection import (
    train,
    recognize_face,
    read_and_preprocess
)
from django.conf import settings
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
import os 
import json

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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            # attach user to project and make admin
            project = Project.objects.get(id=serializer.data['id'])
            user = User.objects.get(id=self.request.user.id)
            ProjectUserRelationship.objects.create(
                user = user,
                project = project,
                is_admin = True
            )

            return Response(
                {"message": "Project created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, project_id, *args, **kwargs):
        obj = ProjectUserRelationship.objects.filter(user__id=self.request.user.id, project__id=project_id)
        if obj.exists():
            project = get_object_or_404(Project, id=project_id)
            serializer = ProjectSerializer(project)
            res = serializer.data
            res.update({"is_admin": obj[0].is_admin})
            return Response(res, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, project_id):
        obj = ProjectUserRelationship.objects.get(user__id=self.request.user.id, project__id=project_id)
        if not obj.exists() and obj.is_admin == False:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if project.users.filter(id=self.request.user.id).exists():
            project.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class ProjectUserManagerView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProjectAdmin]

    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        users = project.users.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, project_id, user_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        user = get_object_or_404(User, id=user_id)
        try:
            relation = ProjectUserRelationship.objects.get(
                user = user,
                project = project
            )
        except ProjectUserRelationship.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        relation.delete()
        return Response(status=status.HTTP_200_OK)
    
class ProjectUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #leave project
    def delete(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        user = get_object_or_404(User, id=self.request.user.id)
        try:
            relation = ProjectUserRelationship.objects.get(
                user = user,
                project = project
            )
        except ProjectUserRelationship.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        relation.delete()
        return Response(status=status.HTTP_200_OK)

class AdminPermissionView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProjectAdmin]

    def post(self, request, project_id, user_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        user = get_object_or_404(User, id=user_id)
        try:
            relation = ProjectUserRelationship.objects.get(
                user = user,
                project = project
            )
        except ProjectUserRelationship.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        relation.is_admin = True
        relation.save()
        return Response(status=status.HTTP_200_OK)
    
    def delete(self, request, project_id, user_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        user = get_object_or_404(User, id=user_id)
        try:
            relation = ProjectUserRelationship.objects.get(
                user = user,
                project = project
            )
        except ProjectUserRelationship.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        relation.is_admin = False
        relation.save()
        return Response(status=status.HTTP_200_OK)
    
class ProjectsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated, IsProjectAdmin]

    def post(self, request, project_id):
        self.permission_classes = [IsProjectAdmin]

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

class ListInvitesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # get all invites for the logged in user
    def get(self, request):
        invites = ProjectInviteToken.objects.filter(user__id=self.request.user.id)
        print(self.request.user)
        serializer = ProjectInviteTokenSerializer(invites, many=True)

        #also return accept and reject links for all invites
        for i in serializer.data:
            i['accept_link'] = f"{request.get_host()}/api/invite/accept/{i['project']}/{i['token']}/"
            i['decline_link'] = f"{request.get_host()}/api/invite/decline/{i['project']}/{i['token']}/"

        # expand project data
        for i in serializer.data:
            project = Project.objects.get(id=i['project'])
            i['project'] = ProjectSerializer(project).data

        return Response(serializer.data, status=status.HTTP_200_OK)

class InviteAcceptView(APIView):

      def get(self, request, project_id, token):
        obj = ProjectInviteToken.objects.filter(token=token)
        if len(obj) == 0:
            return Response({"detail": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)
        invite_obj = obj[0]

        user = invite_obj.user
        try:
            project = Project.objects.get(
                id = project_id
            )
        except Project.DoesNotExist:
            invite_obj.delete()
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            proj = ProjectUserRelationship.objects.create(
                user = user,
                project = project,
            )
        except:
            invite_obj.delete()
            return Response({"detail": "You are already a part of this project"}, status=status.HTTP_200_OK)

        invite_obj.delete()
        return Response({"detail": "Added to project successful"}, status=status.HTTP_200_OK)
      

class InviteDeclineView(APIView):
    def get(self, request, project_id, token):
        try:
            objects = ProjectInviteToken.objects.filter(token=token)
            invite_obj = objects[0]
        except ProjectInviteToken.DoesNotExist:
            return Response({"detail": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)

        invite_obj.delete()
        return Response({"detail": "Successfully declined"}, status=status.HTTP_200_OK)

# api endpoint to get active user data with exception handling
class ActiveUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # do not use UserSerializer from serializers.py
        # it will expose the password
        serializer = UserSerializer(user, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class FaceRegisterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')

        project = get_object_or_404(Project, id=project_id)

        a = Entry.objects.create(
            project = project,
        )

        jsoned = request.data.get('fields')
        jsoned = json.loads(jsoned)

        for i in jsoned:
            b = EntryDetails.objects.create(
                entry = a,
                kv_key = i.get('kv_key'),
                kv_value = i.get('kv_value'),
                kv_type = i.get('kv_type'),
            )

        for file_name, file_obj in request.FILES.items():
            c = EntryImage(
                entry = a
            )
            c.image.upload_to = f"images/{project_id}/"
            if not file_name.endswith('.'):
                file_name += '.' + file_obj.name.split('.')[-1]
            c.image.save(file_name, file_obj) 
            c.save()

        return Response({}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, project_id, entry_id):
        # delete all entries and images
        project = Project.objects.get(id=project_id)

        if not project:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        entries = Entry.objects.get(project=project, entry_id=entry_id)

        if not entries:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # get entryimages and delete them
        images = EntryImage.objects.filter(entry=entries)
        for image in images:
            image.image.delete()
            image.delete()

        entries.delete()

        return Response(status=status.HTTP_200_OK)

class FaceScanView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        base_image_folder = os.path.join(settings.BASE_DIR, 'images', 'images')
        folder = os.path.join(base_image_folder, str(project_id))
        # print(type(request.FILES['test'].read()))

        project = get_object_or_404(Project, id=project_id)
        
        model, paths = train([folder])
        predicted_name = recognize_face(
            read_and_preprocess(request.FILES['test'].read()), 
            model['projected_faces'], 
            model['eigenfaces'], 
            model['mean_face']
        )

        if predicted_name == -1:
            activity_data = {
                "name": "Entity Scanned",
                "success": False if predicted_name == -1 else True
            }

            ProjectActivity.objects.create(
                activity_type = "scanned-entity",
                activity_data = activity_data,
                project = project
            )

            return Response("Entity not found!", status=status.HTTP_400_BAD_REQUEST)
        
        file_name = paths[predicted_name]
        split = file_name.split('\\')[-4:]

        ei = EntryImage.objects.filter(
            image__icontains = split[-1]
        ).first()
        
        if ei:
            serializer = EntrySerializer(ei.entry)

        activity_data = {
            "name": "Entity Scanned",
            "info": serializer.data if ei is not None else None,
            "success": False if predicted_name == -1 else True
        }

        ProjectActivity.objects.create(
            activity_type = "scanned-entity",
            activity_data = activity_data,
            project = project
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

