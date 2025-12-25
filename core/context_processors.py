from django.conf import settings
from notifications.models import Notification

def site_settings(request):
    return {
        'site_name': settings.SITE_NAME,
        'site_domain': settings.SITE_DOMAIN,
        'debug': settings.DEBUG,
    }

def user_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        return {
            'unread_notifications': unread_count,
            'recent_notifications': recent_notifications,
        }
    return {}