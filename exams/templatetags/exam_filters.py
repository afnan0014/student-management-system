from django import template

register = template.Library()

@register.filter
def get_exam_name(exams, exam_id):
    return exams.get(id=exam_id).name if exams.filter(id=exam_id).exists() else "Unknown Exam"

@register.filter
def get_subject_name(subjects, subject_id):
    return subjects.get(id=subject_id).name if subjects.filter(id=subject_id).exists() else "Unknown Subject"

@register.filter
def calculate_grade(marks):
    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return 'N/A'

    if marks >= 90:
        return 'A+'
    elif marks >= 80:
        return 'A'
    elif marks >= 70:
        return 'B+'
    elif marks >= 60:
        return 'B'
    elif marks >= 50:
        return 'C'
    else:
        return 'F'