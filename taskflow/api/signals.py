from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Task, TaskStatusHistory, Notification


def _create_notification(recipient, actor, notif_type, title, message, task=None, project=None):
    if recipient == actor:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notif_type=notif_type,
        title=title,
        message=message,
        task=task,
        project=project,
    )


@receiver(pre_save, sender=Task)
def capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = Task.objects.get(pk=instance.pk).status
            instance._old_assigned = Task.objects.get(pk=instance.pk).assigned_to
        except Task.DoesNotExist:
            instance._old_status = None
            instance._old_assigned = None
    else:
        instance._old_status = None
        instance._old_assigned = None


@receiver(post_save, sender=Task)
def handle_task_changes(sender, instance, created, **kwargs):
    task = instance
    actor = getattr(task, '_current_user', None)

    if created:
        if task.assigned_to and task.assigned_to != task.created_by:
            _create_notification(
                recipient=task.assigned_to,
                actor=task.created_by,
                notif_type='task_assigned',
                title='New task assigned to you',
                message=f'{task.created_by.username} assigned you "{task.title}" in {task.project.name}.',
                task=task,
                project=task.project,
            )
        return

    old_status = getattr(task, '_old_status', None)
    old_assigned = getattr(task, '_old_assigned', None)

    if old_status and old_status != task.status:
        # Log history
        TaskStatusHistory.objects.create(
            task=task,
            changed_by=actor,
            old_status=old_status,
            new_status=task.status,
        )

        status_labels = {
            'pending': '⏳ Pending', 'todo': '📋 To Do', 'ongoing': '🔄 Ongoing',
            'in_review': '🔍 In Review', 'completed': '✅ Completed',
            'blocked': '🚫 Blocked', 'dismissed': '❌ Dismissed',
        }
        old_label = status_labels.get(old_status, old_status)
        new_label = status_labels.get(task.status, task.status)
        changer = actor.username if actor else 'Someone'

        notif_msg = f'{changer} changed "{task.title}" from {old_label} → {new_label} in {task.project.name}.'

        if task.created_by:
            _create_notification(
                recipient=task.created_by,
                actor=actor,
                notif_type='task_status_changed',
                title=f'Task status updated: {new_label}',
                message=notif_msg,
                task=task,
                project=task.project,
            )

        if task.assigned_to and task.assigned_to != task.created_by:
            _create_notification(
                recipient=task.assigned_to,
                actor=actor,
                notif_type='task_status_changed',
                title=f'Task status updated: {new_label}',
                message=notif_msg,
                task=task,
                project=task.project,
            )

    if old_assigned != task.assigned_to:
        if task.assigned_to:
            _create_notification(
                recipient=task.assigned_to,
                actor=actor,
                notif_type='task_assigned',
                title='Task assigned to you',
                message=f'{actor.username if actor else "Admin"} assigned you "{task.title}" in {task.project.name}.',
                task=task,
                project=task.project,
            )
        if old_assigned:
            _create_notification(
                recipient=old_assigned,
                actor=actor,
                notif_type='task_assigned',
                title='You were unassigned from a task',
                message=f'You have been removed from "{task.title}" in {task.project.name}.',
                task=task,
                project=task.project,
            )