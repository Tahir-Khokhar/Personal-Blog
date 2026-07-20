from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from apps.notifications.models import Notification


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).select_related('post')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_as_read_view(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
    return redirect('notifications')


@login_required
def mark_all_as_read_view(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')
