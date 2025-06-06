# Generated by Django 5.2.1 on 2025-06-05 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0002_remove_assignment_updated_at_assignment_subject_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='assignments/files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='assignments/images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='submissions/files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='submissions/images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='assignment_type',
            field=models.CharField(choices=[('individual', 'Individual Work'), ('group', 'Group Work')], default='individual', max_length=20),
        ),
        migrations.AddField(
            model_name='assignment',
            name='files',
            field=models.ManyToManyField(blank=True, related_name='assignment_files', to='assignments.assignmentfile'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='assignment_images', to='assignments.assignmentimage'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='links',
            field=models.ManyToManyField(blank=True, related_name='assignment_links', to='assignments.assignmentlink'),
        ),
        migrations.AddField(
            model_name='submission',
            name='files',
            field=models.ManyToManyField(blank=True, related_name='submission_files', to='assignments.submissionfile'),
        ),
        migrations.AddField(
            model_name='submission',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='submission_images', to='assignments.submissionimage'),
        ),
    ]
