from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Room, RoomTask, Machine, RoomMembership, TaskSubmission, MachineSubmission, MachineRating


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['rank', 'points', 'avatar', 'completed_machines']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    flags_captured = serializers.SerializerMethodField()
    rooms_joined = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'profile', 'flags_captured', 'rooms_joined', 'is_superuser', 'is_staff']

    def get_flags_captured(self, obj):
        return TaskSubmission.objects.filter(user=obj).count() + \
               MachineSubmission.objects.filter(user=obj).count()

    def get_rooms_joined(self, obj):
        return list(RoomMembership.objects.filter(user=obj).values_list('room_id', flat=True))


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user


class RoomTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomTask
        fields = ['id', 'title', 'description', 'points', 'order']
        # flag is excluded for security


class RoomSerializer(serializers.ModelSerializer):
    tasks = RoomTaskSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'category', 'difficulty', 'tags',
                  'rating', 'members_count', 'image', 'creator_name', 'created_at', 'tasks']


class MachineSerializer(serializers.ModelSerializer):
    total_points = serializers.ReadOnlyField()
    user_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    user_completed = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = ['id', 'name', 'os', 'difficulty', 'description', 'tags', 'rating',
                  'user_points', 'root_points', 'total_points', 'ip_address',
                  'release_date', 'retired', 'image', 'solves_count', 'tasks', 'walkthrough_url', 
                  'download_url', 'user_rating', 'rating_count', 'user_completed']

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = MachineRating.objects.filter(user=request.user, machine=obj).first()
            return rating.rating if rating else None
        return None

    def get_rating_count(self, obj):
        return MachineRating.objects.filter(machine=obj).count()

    def get_user_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.completed_machines and isinstance(profile.completed_machines, list):
                    return obj.id in profile.completed_machines
            except UserProfile.DoesNotExist:
                pass
            except Exception:
                pass
        return False

    def get_rating_count(self, obj):
        return MachineRating.objects.filter(machine=obj).count()


class MachineRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineRating
        fields = ['id', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    rank = serializers.CharField(source='profile.rank', read_only=True)
    points = serializers.IntegerField(source='profile.points', read_only=True)
    avatar = serializers.CharField(source='profile.avatar', read_only=True)
    flags_captured = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'rank', 'points', 'avatar', 'flags_captured']

    def get_flags_captured(self, obj):
        return TaskSubmission.objects.filter(user=obj).count() + \
               MachineSubmission.objects.filter(user=obj).count()
