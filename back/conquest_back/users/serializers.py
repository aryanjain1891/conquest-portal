from rest_framework import serializers
from .models import UserProfile,Startup, User,Connection,StartUpMember


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','email','first_name','last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model = UserProfile
        fields = '__all__'

class StartupSerializer(serializers.ModelSerializer):
    user_profile=UserProfileSerializer()
    under_guidance_of=UserProfileSerializer(many=True,read_only=True)
    startup_poc=UserProfileSerializer()
    startup_champion=UserProfileSerializer()
    class Meta:
        model=Startup
        fields='__all__'

class ConnectionSerializer(serializers.ModelSerializer):
    from_user=UserProfileSerializer()
    to_user=UserProfileSerializer()
    class Meta:
        model=Connection
        fields="__all__"

class StartupTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model=StartUpMember
        fields=["id",
                "name",
                "position",
                "profile_pic",
                "linkedin"]
        

class StartupDetailSerializer(serializers.ModelSerializer):
    team_members=StartupTeamSerializer(many=True,read_only=True)
    user_profile=UserProfileSerializer()
    under_guidance_of=UserProfileSerializer(many=True,read_only=True)
    startup_poc=UserProfileSerializer()
    startup_champion=UserProfileSerializer()
    class Meta:
        model=Startup
        fields="__all__"
