from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from courses.models import Department, Course

from reportlab.pdfgen import canvas
from io import BytesIO
import csv

def report_dashboard(request):
    students = User.objects.filter(groups__name='Student')
    staff = User.objects.filter(groups__name='Staff')
    departments = Department.objects.count()
    courses = Course.objects.count()
    
    return render(request, 'reports/report_dashboard.html', {
        'students': students,
        'staff': staff,
        'department_count': departments,
        'course_count': courses
    })

def export_students_csv(request):
    students = User.objects.filter(groups__name='Student')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email'])
    
    for student in students:
        writer.writerow([student.username, student.email])
    
    return response

def export_students_pdf(request):
    students = User.objects.filter(groups__name='Student')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students.pdf"'
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica", 14)
    pdf.drawString(100, 800, "Student Report")
    
    y = 760
    for student in students:
        pdf.drawString(100, y, f"{student.username} - {student.email}")
        y -= 20
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 14)
            y = 800
    
    pdf.save()
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type='application/pdf')
