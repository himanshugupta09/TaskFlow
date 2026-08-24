from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import connection, timezone
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .models import (
    Project, ProjectMember, Task, TaskComment,
    TaskStatusHistory, Notification, ProjectInvite,
)
from .serializers import (
    UserSerializer, RegisterSerializer,
    ProjectSerializer, ProjectMemberSerializer,
    TaskSerializer, TaskCommentSerializer, TaskStatusHistorySerializer,
    NotificationSerializer, ProjectInviteSerializer,
)


def index(request):
    return render(request, 'index.html')


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    s = RegisterSerializer(data=request.data)
    if s.is_valid():
        user = s.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=201)
    return Response(s.errors, status=400)


@api_view(['GET'])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
def dashboard(request):
    project_ids = ProjectMember.objects.filter(
        user=request.user
    ).values_list('project_id', flat=True)

    all_tasks = Task.objects.filter(project_id__in=project_ids)
    my_tasks  = all_tasks.filter(assigned_to=request.user)
    today     = timezone.now().date()

    status_counts = {}
    for t in my_tasks:
        status_counts[t.status] = status_counts.get(t.status, 0) + 1

    return Response({
        'total_projects': len(project_ids),
        'total_tasks':    all_tasks.count(),
        'my_tasks':       my_tasks.count(),
        'overdue':        my_tasks.exclude(
            status__in=['completed', 'dismissed']
        ).filter(due_date__lt=today).count(),
        'status_counts':  status_counts,
        'unread_notifications': Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
    })



@api_view(['GET'])
def search_users(request):
    q = request.query_params.get('q', '').strip()
    if len(q) < 2:
        return Response([])
    users = User.objects.filter(
        Q(email__icontains=q) | Q(username__icontains=q)
    ).exclude(id=request.user.id)[:8]
    return Response(UserSerializer(users, many=True).data)



@api_view(['GET'])
def notifications_list(request):
    notifs = Notification.objects.filter(recipient=request.user)[:50]
    return Response(NotificationSerializer(notifs, many=True).data)


@api_view(['GET'])
def notifications_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'count': count})


@api_view(['POST'])
def notifications_mark_read(request):
    ids = request.data.get('ids') 
    qs  = Notification.objects.filter(recipient=request.user, is_read=False)
    if ids:
        qs = qs.filter(id__in=ids)
    qs.update(is_read=True)
    return Response({'marked': qs.count()})


@api_view(['DELETE'])
def notification_delete(request, pk):
    Notification.objects.filter(id=pk, recipient=request.user).delete()
    return Response(status=204)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class   = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ids = ProjectMember.objects.filter(
            user=self.request.user
        ).values_list('project_id', flat=True)
        return Project.objects.filter(id__in=ids)

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        ProjectMember.objects.create(project=project, user=self.request.user, role='admin')

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.created_by != request.user:
            return Response({'error': 'Only the project creator can delete it'}, status=403)
        project.delete()
        return Response(status=204)

    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        project = self.get_object()
        return Response(ProjectMemberSerializer(project.members.all(), many=True).data)

    @action(detail=True, methods=['delete'], url_path='members/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        project = self.get_object()
        if not ProjectMember.objects.filter(project=project, user=request.user, role='admin').exists():
            return Response({'error': 'Admin only'}, status=403)
        ProjectMember.objects.filter(id=member_id, project=project).delete()
        return Response(status=204)

    @action(detail=True, methods=['get', 'post'], url_path='tasks')
    def tasks(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            qs = project.tasks.all()
            if request.query_params.get('status'):
                qs = qs.filter(status=request.query_params['status'])
            return Response(TaskSerializer(qs, many=True).data)

        s = TaskSerializer(data=request.data)
        if s.is_valid():
            assigned_id = s.validated_data.pop('assigned_to_id', None)
            assigned    = User.objects.filter(id=assigned_id).first() if assigned_id else None
            task        = s.save(project=project, created_by=request.user, assigned_to=assigned)
            task._current_user = request.user
            task.save()
            return Response(TaskSerializer(task).data, status=201)
        return Response(s.errors, status=400)




class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_ids = ProjectMember.objects.filter(
            user=self.request.user
        ).values_list('project_id', flat=True)
        
        queryset = Task.objects.filter(project_id__in=project_ids)

        status_param = self.request.query_params.get('status')
        assignee_param = self.request.query_params.get('assignee')
        due_date_after = self.request.query_params.get('due_date_after')
        due_date_before = self.request.query_params.get('due_date_before')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if assignee_param:
            queryset = queryset.filter(assigned_to_id=assignee_param)
        if due_date_after:
            queryset = queryset.filter(due_date__gte=due_date_after)
        if due_date_before:
            queryset = queryset.filter(due_date__lte=due_date_before)

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        query_string = request.GET.urlencode()
        cache_key = f"tasks_user_{request.user.id}_{query_string}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 10)
        return response
    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        self._invalidate_project_task_caches(task.project_id)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        old_status = task.status
        old_assignee = task.assigned_to

        partial = kwargs.pop('partial', False)
        s = TaskSerializer(task, data=request.data, partial=partial)
        
        if s.is_valid():
            assigned_id = s.validated_data.pop('assigned_to_id', -1)
            if assigned_id != -1:
                s.validated_data['assigned_to'] = (
                    User.objects.filter(id=assigned_id).first() if assigned_id else None
                )

            instance = s.save()
            instance._current_user = request.user
            instance.save()

            self._invalidate_project_task_caches(instance.project_id)

            if instance.status != old_status:
                recipients = {instance.created_by, instance.assigned_to} - {None, request.user}
                for recipient in recipients:
                    send_notification_task.delay(
                        recipient_id=recipient.id,
                        title=f'Task Status Updated: "{instance.title}"',
                        message=f'Status changed from "{old_status}" to "{instance.status}".',
                        task_id=instance.id,
                    )

            if instance.assigned_to and instance.assigned_to != old_assignee:
                send_notification_task.delay(
                    recipient_id=instance.assigned_to.id,
                    title='New Task Assigned',
                    message=f'You were assigned to task: "{instance.title}".',
                    task_id=instance.id,
                )

            return Response(TaskSerializer(instance).data)

        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        is_admin = ProjectMember.objects.filter(
            project=task.project, user=request.user, role='admin'
        ).exists()

        if task.created_by != request.user and not is_admin:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        project_id = task.project_id
        task.delete()

        self._invalidate_project_task_caches(project_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == 'GET':
            return Response(TaskCommentSerializer(task.comments.all(), many=True).data)

        s = TaskCommentSerializer(data=request.data)
        if s.is_valid():
            comment = s.save(task=task, author=request.user)

            recipients = {task.created_by, task.assigned_to} - {None, request.user}
            for recipient in recipients:
                send_notification_task.delay(
                    recipient_id=recipient.id,
                    title=f'New comment on "{task.title}"',
                    message=f'{request.user.username} commented: "{comment.text[:80]}"',
                    task_id=task.id,
                )

            return Response(s.data, status=status.HTTP_201_CREATED)

        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        task = self.get_object()
        h = TaskStatusHistory.objects.filter(task=task)
        return Response(TaskStatusHistorySerializer(h, many=True).data)

    def _invalidate_project_task_caches(self, project_id):
        member_user_ids = ProjectMember.objects.filter(
            project_id=project_id
        ).values_list('user_id', flat=True)

        for user_id in member_user_ids:
            cache.delete_pattern(f"tasks_user_{user_id}_*")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_to_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=404)

    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)

    if not ProjectMember.objects.filter(project=project, user=request.user, role='admin').exists():
        return Response({'error': 'Admin only'}, status=403)

    email = request.data.get('email', '').strip().lower()
    role  = request.data.get('role', 'member')
    if not email:
        return Response({'error': 'Email is required'}, status=400)

    if '@' not in email or len(email) < 5:
        return Response({'error': 'Invalid email format'}, status=400)

    existing = User.objects.filter(email=email).first()
    if existing:
        if ProjectMember.objects.filter(project=project, user=existing).exists():
            return Response({'error': 'User is already a member'}, status=400)
        ProjectMember.objects.create(project=project, user=existing, role=role)
        Notification.objects.create(
            recipient  = existing,
            actor      = request.user,
            notif_type = 'project_member_added',
            title      = f'You were added to {project.name}',
            message    = f'{request.user.username} added you to "{project.name}" as {role}.',
            project    = project,
        )
        return Response({'status': 'added', 'message': f'{existing.username} added directly', 'user': UserSerializer(existing).data})

    import uuid as _uuid
    invite, created = ProjectInvite.objects.get_or_create(
        project=project, email=email,
        defaults={'invited_by': request.user, 'role': role}
    )
    if not created:
        if invite.status == 'accepted':
            return Response({'error': 'This email already accepted an invite'}, status=400)
        invite.token  = _uuid.uuid4()
        invite.status = 'pending'
        invite.role   = role
        invite.save()

    invite_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/invite/{invite.token}"
    send_mail(
        subject=f"You're invited to join {project.name} on TaskFlow",
        message=f"""{request.user.username} invited you to "{project.name}".

Accept your invite here:
{invite_url}

This link lets you create an account and join the project automatically.
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
    return Response({'status': 'invited', 'message': f'Invite sent to {email}', 'invite_token': str(invite.token)})


@api_view(['GET'])
@permission_classes([AllowAny])
def invite_info(request, token):
    try:
        invite = ProjectInvite.objects.select_related('project').get(token=token)
    except ProjectInvite.DoesNotExist:
        return Response({'error': 'Invalid invite link'}, status=404)
    if invite.status == 'accepted':
        return Response({'error': 'Invite already used'}, status=400)
    return Response({
        'project_name': invite.project.name,
        'email':        invite.email,
        'role':         invite.role,
        'invited_by':   invite.project.created_by.username,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invite(request, token):
    try:
        invite = ProjectInvite.objects.select_related('project').get(token=token, status='pending')
    except ProjectInvite.DoesNotExist:
        return Response({'error': 'Invalid or expired invite'}, status=400)

    user = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        from rest_framework_simplejwt.tokens import AccessToken
        try:
            payload = AccessToken(auth_header.split(' ')[1])
            user    = User.objects.get(id=payload['user_id'])
        except Exception:
            pass

    if not user:
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        s.validated_data['email'] = invite.email
        user = s.save()

    ProjectMember.objects.get_or_create(
        project=invite.project, user=user,
        defaults={'role': invite.role}
    )
    invite.status = 'accepted'
    invite.save()

    Notification.objects.create(
        recipient  = user,
        actor      = invite.invited_by,
        notif_type = 'project_member_added',
        title      = f'Welcome to {invite.project.name}!',
        message    = f'You have joined "{invite.project.name}" as {invite.role}.',
        project    = invite.project,
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        'message':    f'You joined {invite.project.name}!',
        'project_id': invite.project.id,
        'user':       UserSerializer(user).data,
        'access':     str(refresh.access_token),
        'refresh':    str(refresh),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_invites(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    if not ProjectMember.objects.filter(project=project, user=request.user, role='admin').exists():
        return Response({'error': 'Admin only'}, status=403)
    invites = ProjectInvite.objects.filter(project=project).order_by('-created_at')
    return Response(ProjectInviteSerializer(invites, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_invite(request, project_id, invite_id):
    if not ProjectMember.objects.filter(project_id=project_id, user=request.user, role='admin').exists():
        return Response({'error': 'Admin only'}, status=403)
    ProjectInvite.objects.filter(id=invite_id, project_id=project_id).delete()
    return Response(status=204)



@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):

    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown"
    }
    
    try:
        connection.ensure_connection()
        health_status["database"] = "connected"
    except Exception:
        health_status["database"] = "disconnected"
        health_status["status"] = "unhealthy"
    try:
        cache.set('health_check', 'ok', timeout=5)
        if cache.get('health_check') == 'ok':
            health_status["redis"] = "connected"
    except Exception:
        health_status["redis"] = "disconnected"
        health_status["status"] = "unhealthy"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return Response(health_status, status=status_code)



@api_view(['GET'])
@permission_classes([AllowAny])
def metrics(request):

    return Response({
        "total_projects": Project.objects.count(),
        "total_tasks": Task.objects.count(),
        "total_notifications_sent": Notification.objects.count()
    })

