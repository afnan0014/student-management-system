from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import landing_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_view, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('courses/', include('courses.urls')),
    path('reports/', include('reports.urls')), 
    path('exams/', include('exams.urls')), 
    path('timetable/', include('timetable.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
