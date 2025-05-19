from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('hod/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('add-user/', views.add_user, name='add_user'),
    path('view-users/<str:role>/', views.view_users_by_role, name='view_users_by_role'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-user-password/<int:user_id>/', views.change_user_password, name='change_user_password'),

]
