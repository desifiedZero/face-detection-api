from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import Entry, EntryDetails, Project, ProjectActivity


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    storageSchema = serializers.JSONField(required=True)
    registered = serializers.SerializerMethodField('get_registered')

    def get_registered(self, obj):
        return obj.entry_set.all().count()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'storageSchema', 'registered']

class EntrySerializer(serializers.ModelSerializer):
    entry_details = serializers.SerializerMethodField('get_entry_details')
    image = serializers.SerializerMethodField('get_image')

    def get_entry_details(self, obj):
        return EntryDetailsSerializer(obj.entries.all(), many=True).data
    
    def get_image(self, obj):
        return obj.images.first().image.url

    class Meta:
        model = Entry
        fields = ['entry_id', 'image', 'entry_details']

class EntryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryDetails
        fields = ['entry_detail_id', 'kv_key', 'kv_value', 'kv_type']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user
    
class ProjectActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectActivity
        fields = ['activity_type', 'activity_data', 'project_activity_id', 'created_at']