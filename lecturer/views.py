from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Avg
from django.core.paginator import Paginator

from .models import LecturerProfile, LecturerCourse, Announcement
from course.models import Course, CourseModule, LearningMaterial
from student.models import Assignment, Enrollment
from accounts.models import User, Notification

from .forms import AnnouncementForm, CourseForm, CourseModuleForm, LearningMaterialForm, AssignmentGradingForm, AssignmentCreationForm

def lecturer_required(view_func):
    """Decorator to check if the user is a lecturer"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.user_type != 'lecturer':
            return HttpResponseForbidden("You must be a lecturer to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@lecturer_required
def dashboard(request):
    """Lecturer dashboard showing course statistics and recent activities"""
    try:
        lecturer_profile = request.user.lecturer_profile
    except LecturerProfile.DoesNotExist:
        # Create profile if it doesn't exist
        lecturer_profile = LecturerProfile.objects.create(
            user=request.user,
            staff_id=f"STAFF{request.user.id}",
            department="Not Specified"
        )
    
    # Get courses taught by lecturer
    lecturer_courses = LecturerCourse.objects.filter(lecturer=lecturer_profile)
    courses = [lc.course for lc in lecturer_courses]
    
    # Get statistics
    course_count = len(courses)
    student_count = Enrollment.objects.filter(course__in=courses).values('student').distinct().count()
    assignment_count = Assignment.objects.filter(course__in=courses).count()
    pending_assignments = Assignment.objects.filter(course__in=courses, score__isnull=True).count()
    
    # Recent announcements
    recent_announcements = Announcement.objects.filter(lecturer=lecturer_profile).order_by('-posted_at')[:5]
    
    context = {
        'lecturer_profile': lecturer_profile,
        'course_count': course_count,
        'student_count': student_count,
        'assignment_count': assignment_count,
        'pending_assignments': pending_assignments,
        'recent_announcements': recent_announcements,
        'courses': courses[:5],  # Show only 5 recent courses
    }
    
    return render(request, 'lecturer/dashboard.html', context)

@login_required
@lecturer_required
def course_list(request):
    """Display all courses taught by the lecturer"""
    lecturer_profile = request.user.lecturer_profile
    lecturer_courses = LecturerCourse.objects.filter(lecturer=lecturer_profile).select_related('course')
    
    # Get enrollment counts for each course
    for lc in lecturer_courses:
        lc.enrollment_count = Enrollment.objects.filter(course=lc.course).count()
    
    context = {
        'lecturer_courses': lecturer_courses,
    }
    
    return render(request, 'lecturer/course_list.html', context)

@login_required
@lecturer_required
def create_course(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            # Assign lecturer to the course
            LecturerCourse.objects.create(
                lecturer=request.user.lecturer_profile,
                course=course,
                is_primary=True
            )
            messages.success(request, f"Course '{course.title}' created successfully!")
            return redirect('lecturer:course_detail', course_id=course.id)
    else:
        form = CourseForm()
    
    context = {
        'form': form,
        'title': 'Create New Course',
    }
    
    return render(request, 'lecturer/course_form.html', context)

@login_required
@lecturer_required
def course_detail(request, course_id):
    """View course details and management options"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=course).exists():
        return HttpResponseForbidden("You do not have permission to view this course.")
    
    # Get modules, announcements, and enrollments
    modules = CourseModule.objects.filter(course=course).order_by('order')
    announcements = Announcement.objects.filter(course=course).order_by('-posted_at')
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    
    # Get assignment statistics
    assignments = Assignment.objects.filter(course=course)
    pending_assignments = assignments.filter(score__isnull=True).count()
    
    context = {
        'course': course,
        'modules': modules,
        'announcements': announcements,
        'enrollments': enrollments,
        'assignment_count': assignments.count(),
        'pending_assignments': pending_assignments,
    }
    
    return render(request, 'lecturer/course_detail.html', context)

@login_required
@lecturer_required
def edit_course(request, course_id):
    """Edit course details"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=course).exists():
        return HttpResponseForbidden("You do not have permission to edit this course.")
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully!")
            return redirect('lecturer:course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'title': 'Edit Course',
        'course': course,
    }
    
    return render(request, 'lecturer/course_form.html', context)

@login_required
@lecturer_required
def create_announcement(request, course_id):
    """Create a new announcement for a course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=course).exists():
        return HttpResponseForbidden("You do not have permission to make announcements for this course.")
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.lecturer = request.user.lecturer_profile
            announcement.course = course
            announcement.save()
            
            # Create notifications for all enrolled students
            enrollments = Enrollment.objects.filter(course=course)
            for enrollment in enrollments:
                Notification.objects.create(
                    user=enrollment.student.user,
                    title=f"New Announcement: {course.code}",
                    message=f"A new announcement '{announcement.title}' has been posted in {course.title}."
                )
            
            messages.success(request, "Announcement published successfully!")
            return redirect('lecturer:course_detail', course_id=course.id)
    else:
        form = AnnouncementForm()
    
    context = {
        'form': form,
        'course': course,
    }
    
    return render(request, 'lecturer/announcement_form.html', context)

@login_required
@lecturer_required
def manage_assignments(request, course_id):
    """Manage and grade student assignments for a course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    lecturer_profile = request.user.lecturer_profile
    get_object_or_404(LecturerCourse, lecturer=lecturer_profile, course=course)
    
    # Get all assignment announcements (the ones created by lecturers)
    assignment_announcements = Announcement.objects.filter(
        course=course,
        title__startswith="New Assignment:"
    ).order_by('-posted_at')
    
    # Get all assignment submissions (from students)
    student_submissions = Assignment.objects.filter(course=course).select_related('student__user')
    
    # Get stats for display
    total_submissions = student_submissions.count()
    graded_count = student_submissions.filter(score__isnull=False).count()
    pending_count = total_submissions - graded_count
    
    # Calculate average score of graded assignments
    graded_submissions = student_submissions.filter(score__isnull=False)
    average_score = graded_submissions.aggregate(Avg('score'))['score__avg'] if graded_submissions.exists() else 0
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter == 'pending':
        student_submissions = student_submissions.filter(score__isnull=True)
    elif status_filter == 'graded':
        student_submissions = student_submissions.filter(score__isnull=False)
    
    # Pagination for student submissions
    paginator = Paginator(student_submissions, 10)  # 10 assignments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'course': course,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_assignments': total_submissions,
        'pending_count': pending_count,
        'graded_count': graded_count,
        'average_score': average_score,
        'assignment_announcements': assignment_announcements,  # Add this to context
    }
    
    return render(request, 'lecturer/manage_assignments.html', context)

@login_required
@lecturer_required
def create_assignment(request, course_id):
    """Create a new assignment announcement for a course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    lecturer_profile = request.user.lecturer_profile
    get_object_or_404(LecturerCourse, lecturer=lecturer_profile, course=course)
    
    if request.method == 'POST':
        form = AssignmentCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create an announcement for this assignment
            announcement = Announcement(
                lecturer=lecturer_profile,
                course=course,
                title=f"New Assignment: {form.cleaned_data['title']}",
                content=form.cleaned_data.get('instructions', ''),
            )
            
            # Handle file attachment
            if 'submission' in request.FILES:
                announcement.attachment = request.FILES['submission']
                
            announcement.save()
            
            messages.success(request, f"Assignment '{form.cleaned_data['title']}' has been created successfully!")
            return redirect('lecturer:course_detail', course_id=course.id)
    else:
        form = AssignmentCreationForm()
    
    context = {
        'form': form,
        'course': course,
    }
    
    return render(request, 'lecturer/create_assignment.html', context)

@login_required
@lecturer_required
def grade_assignment(request, assignment_id):
    """Grade a student assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=assignment.course).exists():
        return HttpResponseForbidden("You do not have permission to grade assignments for this course.")
    
    if request.method == 'POST':
        form = AssignmentGradingForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            
            # Notify student
            Notification.objects.create(
                user=assignment.student.user,
                title=f"Assignment Graded: {assignment.course.code}",
                message=f"Your assignment '{assignment.title}' has been graded. Score: {assignment.score}"
            )
            
            messages.success(request, "Assignment graded successfully!")
            return redirect('lecturer:manage_assignments', course_id=assignment.course.id)
    else:
        form = AssignmentGradingForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
    }
    
    return render(request, 'lecturer/grade_assignment.html', context)

@login_required
@lecturer_required
def manage_modules(request, course_id):
    """Manage course modules"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=course).exists():
        return HttpResponseForbidden("You do not have permission to manage modules for this course.")
    
    modules = CourseModule.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'modules': modules,
    }
    
    return render(request, 'lecturer/manage_modules.html', context)

@login_required
@lecturer_required
def create_module(request, course_id):
    """Create a new module for a course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    lecturer_profile = request.user.lecturer_profile
    get_object_or_404(LecturerCourse, lecturer=lecturer_profile, course=course)
    
    # Get the next order number
    next_order = CourseModule.objects.filter(course=course).count() + 1
    
    if request.method == 'POST':
        form = CourseModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.order = request.POST.get('order', next_order)
            module.save()
            
            messages.success(request, f"Module '{module.title}' has been created successfully!")
            return redirect('lecturer:course_detail', course_id=course.id)
    else:
        form = CourseModuleForm(initial={'order': next_order})
    
    context = {
        'form': form,
        'course': course,
    }
    
    return render(request, 'lecturer/create_module.html', context)

@login_required
@lecturer_required
def add_material(request, module_id):
    """Add learning material to a module"""
    module = get_object_or_404(CourseModule, id=module_id)
    course = module.course
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=course).exists():
        return HttpResponseForbidden("You do not have permission to add materials to this course.")
    
    if request.method == 'POST':
        form = LearningMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.module = module
            material.save()
            
            # Notify enrolled students
            enrollments = Enrollment.objects.filter(course=course)
            for enrollment in enrollments:
                Notification.objects.create(
                    user=enrollment.student.user,
                    title=f"New Learning Material: {course.code}",
                    message=f"New material '{material.title}' has been added to module '{module.title}' in {course.title}."
                )
            
            messages.success(request, "Learning material added successfully!")
            return redirect('lecturer:manage_modules', course_id=course.id)
    else:
        form = LearningMaterialForm()
    
    context = {
        'form': form,
        'module': module,
        'course': course,
    }
    
    return render(request, 'lecturer/material_form.html', context)

@login_required
@lecturer_required
def student_list(request, course_id):
    """View list of students enrolled in a course"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verify lecturer teaches this course
    if not LecturerCourse.objects.filter(lecturer=request.user.lecturer_profile, course=course).exists():
        return HttpResponseForbidden("You do not have permission to view students for this course.")
    
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    
    return render(request, 'lecturer/student_list.html', context)

@login_required
@lecturer_required
def profile(request):
    """View and edit lecturer profile"""
    try:
        lecturer_profile = request.user.lecturer_profile
    except LecturerProfile.DoesNotExist:
        lecturer_profile = LecturerProfile.objects.create(
            user=request.user,
            staff_id=f"STAFF{request.user.id}",
            department="Not Specified"
        )
    
    # Count courses, students, etc.
    courses = [lc.course for lc in LecturerCourse.objects.filter(lecturer=lecturer_profile)]
    course_count = len(courses)
    student_count = Enrollment.objects.filter(course__in=courses).values('student').distinct().count()
    
    context = {
        'lecturer_profile': lecturer_profile,
        'course_count': course_count,
        'student_count': student_count,
    }
    
    return render(request, 'lecturer/profile.html', context)
