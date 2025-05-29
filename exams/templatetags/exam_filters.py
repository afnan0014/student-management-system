from django import template

register = template.Library()

@register.filter
def get_exam_name(exams, exam_id):
    return exams.get(id=exam_id).name if exams.filter(id=exam_id).exists() else "Unknown Exam"

@register.filter
def get_subject_name(subjects, subject_id):
    return subjects.get(id=subject_id).name if subjects.filter(id=subject_id).exists() else "Unknown Subject"
