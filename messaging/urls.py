from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('send/', views.send_message, name='send_message'),
    path('send/reply/<int:parent_id>/', views.send_message, name='reply_message'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('admin/messages/<str:message_type>/', views.admin_messages, name='admin_messages'),
    path('edit/<int:message_id>/', views.edit_message, name='edit_message'),
    path('delete/<int:message_id>/', views.delete_message, name='delete_message'),
]