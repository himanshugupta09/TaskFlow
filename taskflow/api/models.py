import uuid
from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name


class ProjectMember(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('member', 'Member')]
    project  = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role     = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('todo',      'To Do'),
        ('ongoing',   'Ongoing'),
        ('in_review', 'In Review'),
        ('completed', 'Completed'),
        ('blocked',   'Blocked'),
        ('dismissed', 'Dismissed'),
    ]
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high',     'High'),
        ('medium',   'Medium'),
        ('low',      'Low'),
    ]

    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    tags        = models.CharField(max_length=300, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    due_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self): return self.title


class TaskComment(models.Model):
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Notification(models.Model):
    TYPE_CHOICES = [
        ('task_status_changed',  'Task Status Changed'),
        ('task_assigned',        'Task Assigned'),
        ('task_commented',       'Task Commented'),
        ('task_overdue',         'Task Overdue'),
        ('project_member_added', 'Added to Project'),
    ]

    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notif_type = models.CharField(max_length=40, choices=TYPE_CHOICES)
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    project    = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient.username} ← {self.notif_type}'


class ProjectInvite(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('expired', 'Expired')]
    project    = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invites')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    email      = models.EmailField()
    role       = models.CharField(max_length=10, choices=ProjectMember.ROLE_CHOICES, default='member')
    token      = models.UUIDField(default=uuid.uuid4, unique=True)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'email')


class TaskStatusHistory(models.Model):
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='status_history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='status_changes')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']