from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('unread/', views.get_unread_notifications, name='get_unread_notifications'),
    path('all/', views.get_all_notifications, name='get_all_notifications'),
    path('toggle-read/<int:notification_id>/', views.toggle_notification_read, name='toggle_notification_read'),
    path('clear-read/', views.clear_read_notifications, name='clear_read_notifications'),  # New endpoint
]