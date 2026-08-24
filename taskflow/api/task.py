import logging
from celery import shared_task
from .models import Notification

logger = logging.getLogger(__name__)

@shared_task
def send_notification_task(recipient_id, title, message, task_id=None):
    try:
        notification = Notification.objects.create(
            recipient_id=recipient_id,
            title=title,
            message=message,
            task_id=task_id,
            is_read=False
        )
        
        logger.info(f"[SIMULATED NOTIFICATION] Delivered to User {recipient_id}: {title} - {message}")
        
        return f"Notification {notification.id} processed successfully."
    except Exception as e:
        logger.error(f"Failed to process notification: {str(e)}")
        raise e