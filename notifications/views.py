from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Notification
from django.http import JsonResponse

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = Notification.objects.filter(id=notification_id, recipient=request.user).first()
    if notification:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        redirect_url = notification.redirect_url
        if not redirect_url:
            # Redirect to the user's dashboard based on their role
            if request.user.groups.filter(name='Admin').exists():
                redirect_url = 'admin_dashboard'
            elif request.user.groups.filter(name='Staff').exists():
                redirect_url = 'staff_dashboard'
            elif request.user.groups.filter(name='Student').exists():
                redirect_url = 'student_dashboard'
            else:
                redirect_url = 'landing'
        return redirect(redirect_url)
    else:
        # Redirect to the user's dashboard if notification is not found
        if request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='Staff').exists():
            return redirect('staff_dashboard')
        elif request.user.groups.filter(name='Student').exists():
            return redirect('student_dashboard')
        else:
            return redirect('landing')

@login_required
def get_unread_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    data = {
        'count': notifications.count(),
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'redirect_url': n.redirect_url,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for n in notifications[:5]
        ]
    }
    return JsonResponse(data)

@login_required
def get_all_notifications(request):
    # Only fetch unread notifications for the dropdown
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
    data = {
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'redirect_url': n.redirect_url,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': n.is_read,
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)

@login_required
def clear_read_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=True).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def toggle_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = Notification.objects.filter(id=notification_id, recipient=request.user).first()
        if notification:
            # Toggle the is_read status
            notification.is_read = not notification.is_read
            # Update read_at timestamp if marking as read, clear it if marking as unread
            notification.read_at = timezone.now() if notification.is_read else None
            notification.save()
            return JsonResponse({'success': True, 'is_read': notification.is_read})
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)