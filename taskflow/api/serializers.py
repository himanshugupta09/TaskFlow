from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, ProjectMember, Task, TaskComment, TaskStatusHistory, Notification, ProjectInvite


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProjectMemberSerializer(serializers.ModelSerializer):
    user     = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model  = ProjectMember
        fields = ['id', 'user', 'username', 'role', 'joined_at']

    def create(self, validated_data):
        username = validated_data.pop('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'username': 'User not found'})
        return ProjectMember.objects.create(user=user, **validated_data)


class TaskCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model  = TaskComment
        fields = ['id', 'author', 'text', 'created_at']
        read_only_fields = ['author']


class TaskStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model  = TaskStatusHistory
        fields = ['id', 'changed_by', 'old_status', 'new_status', 'changed_at']


class NotificationSerializer(serializers.ModelSerializer):
    actor   = UserSerializer(read_only=True)
    task_id = serializers.IntegerField(source='task.id', read_only=True, allow_null=True)

    class Meta:
        model  = Notification
        fields = ['id', 'notif_type', 'title', 'message', 'is_read',
                  'created_at', 'actor', 'task_id', 'project_id']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to    = UserSerializer(read_only=True)
    created_by     = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    is_overdue     = serializers.SerializerMethodField()
    comment_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'tags',
            'assigned_to', 'assigned_to_id', 'created_by',
            'due_date', 'created_at', 'updated_at',
            'is_overdue', 'comment_count', 'project',
        ]
        read_only_fields = ['created_by', 'project']

    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.due_date and obj.status not in ('completed', 'dismissed'):
            return obj.due_date < timezone.now().date()
        return False

    def get_comment_count(self, obj):
        return obj.comments.count()


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members    = ProjectMemberSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()
    my_role    = serializers.SerializerMethodField()
    progress   = serializers.SerializerMethodField()

    class Meta:
        model  = Project
        fields = ['id', 'name', 'description', 'created_by', 'created_at',
                  'members', 'task_count', 'my_role', 'progress']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_my_role(self, obj):
        request = self.context.get('request')
        if request:
            m = obj.members.filter(user=request.user).first()
            return m.role if m else None
        return None

    def get_progress(self, obj):
        total = obj.tasks.count()
        if not total:
            return 0
        done = obj.tasks.filter(status__in=['completed', 'dismissed']).count()
        return round((done / total) * 100)


class ProjectInviteSerializer(serializers.ModelSerializer):
    invited_by = UserSerializer(read_only=True)

    class Meta:
        model  = ProjectInvite
        fields = ['id', 'email', 'role', 'status', 'invited_by', 'created_at', 'token']
        read_only_fields = ['invited_by', 'status', 'token']