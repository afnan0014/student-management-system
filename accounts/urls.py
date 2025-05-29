from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),  # Updated to landing_view
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('users/<str:role>/', views.view_users_by_role, name='view_users_by_role'),
    path('add/<str:role>/', views.add_user, name='add_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    path('bulk-delete/', views.bulk_delete_users, name='bulk_delete_users'),
    path('student-profile/<int:user_id>/', views.student_profile, name='student_profile'),
    path('staff-profile/<int:user_id>/', views.staff_profile, name='staff_profile'),
]