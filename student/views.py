from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime

from .models import StudentProfile, Enrollment, Assignment
from .forms import AssignmentSubmissionForm, EnrollmentRequestForm, StudentProfileForm
from course.models import Course, CourseModule, LearningMaterial
from lecturer.models import Announcement
from accounts.models import Notification

def student_required(view_func):
    """Decorator to check if the user is a student"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.user_type != 'student':
            return HttpResponseForbidden("You must be a student to access this page.")
        
        # Ensure student profile exists
        try:
            # Try to access the student profile
            student_profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            # Create a default profile if it doesn't exist
            student_profile = StudentProfile.objects.create(
                user=request.user,
                registration_number=f"STU{request.user.id}",
                department="Not Specified",
                year_of_study=1
            )
            messages.info(request, "A student profile has been created for you. Please update your details in the profile section.")
            
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@student_required
def dashboard(request):
    """Student dashboard showing enrolled courses and recent activities"""
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        student_profile = StudentProfile.objects.create(
            user=request.user,
            registration_number=f"STU{request.user.id}",
            department="Not Specified",
            year_of_study=1
        )
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(
        student=student_profile, 
        status='approved'
    ).select_related('course').order_by('-enrollment_date')[:5]
    
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    
    # Get recent announcements from enrolled courses
    announcements = Announcement.objects.filter(
        course__in=enrolled_courses
    ).order_by('-posted_at')[:5]
    
    # Get assignments
    assignments = Assignment.objects.filter(
        student=student_profile
    ).order_by('-submitted_at')[:5]
    
    # Get stats
    pending_enrollments = Enrollment.objects.filter(
        student=student_profile, 
        status='pending'
    ).count()
    
    # Assignment statistics
    assignment_count = Assignment.objects.filter(
        student=student_profile
    ).count()
    
    completed_assignment_count = Assignment.objects.filter(
        student=student_profile,
        score__isnull=False
    ).count()
    
    # Calculate semester completion percentage
    current_date = datetime.now()
    semester_start = datetime(current_date.year, 1 if current_date.month < 7 else 7, 1)
    semester_end = datetime(current_date.year, 6 if current_date.month < 7 else 12, 30)
    total_semester_days = (semester_end - semester_start).days
    days_passed = (current_date - semester_start).days
    semester_completion = min(100, max(0, int((days_passed / total_semester_days) * 100)))
    
    context = {
        'student_profile': student_profile,
        'enrollments': enrollments,
        'enrolled_course_count': len(enrolled_courses),
        'announcements': announcements,
        'assignments': assignments,
        'pending_enrollments': pending_enrollments,
        'assignment_count': assignment_count,
        'completed_assignment_count': completed_assignment_count,
        'semester_completion': semester_completion,
    }
    
    return render(request, 'student/dashboard.html', context)

@login_required
@student_required
def course_list(request):
    """Display available courses and allow enrollment"""
    student_profile = request.user.student_profile
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(
        student=student_profile
    ).select_related('course')
    
    enrolled_course_ids = [enrollment.course.id for enrollment in enrollments]
    
    # Get available courses (not enrolled)
    available_courses = Course.objects.filter(
        is_active=True
    ).exclude(
        id__in=enrolled_course_ids
    )
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        available_courses = available_courses.filter(
            Q(title__icontains=search_query) | 
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination for available courses
    paginator = Paginator(available_courses, 8)  # 8 courses per page
    page_number = request.GET.get('page')
    available_courses_page = paginator.get_page(page_number)
    
    context = {
        'enrollments': enrollments,
        'available_courses': available_courses_page,
        'search_query': search_query,
    }
    
    return render(request, 'student/course_list.html', context)

@login_required
@student_required
def course_detail(request, course_id):
    """View course details including modules, materials, and announcements"""
    course = get_object_or_404(Course, id=course_id)
    student_profile = request.user.student_profile
    
    # Check if student is enrolled
    enrollment = get_object_or_404(
        Enrollment, 
        student=student_profile, 
        course=course, 
        status='approved'
    )
    
    # Get course modules and materials
    modules = CourseModule.objects.filter(course=course).order_by('order')
    
    # Get announcements
    announcements = Announcement.objects.filter(course=course).order_by('-posted_at')
    
    # Get assignment announcements (announcements that start with "New Assignment:")
    course_assignments = announcements.filter(title__startswith="New Assignment:")
    
    # Get student's assignments for this course
    assignments = Assignment.objects.filter(
        student=student_profile,
        course=course
    ).order_by('-submitted_at')
    
    # Create a set of assignment IDs that have been submitted
    submitted_assignment_ids = set()
    for assignment in assignments:
        if "New Assignment:" in assignment.title:
            # Extract the announcement ID from the assignment title if possible
            try:
                announcement_id = int(assignment.title.split("ID:")[-1].strip())
                submitted_assignment_ids.add(announcement_id)
            except (ValueError, IndexError):
                # If we can't extract the ID, just skip it
                pass
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'announcements': announcements,
        'assignments': assignments,
        'course_assignments': course_assignments,
        'submitted_assignment_ids': submitted_assignment_ids,
    }
    
    return render(request, 'student/course_detail.html', context)

@login_required
@student_required
def enroll_course(request, course_id):
    """Handle course enrollment requests"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    student_profile = request.user.student_profile
    
    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(
        student=student_profile,
        course=course
    ).first()
    
    if existing_enrollment:
        messages.warning(request, f"You are already enrolled in {course.title}")
        return redirect('student:course_list')
    
    if request.method == 'POST':
        # Automatically approve the enrollment (no lecturer approval needed)
        enrollment = Enrollment(
            student=student_profile,
            course=course,
            status='approved'  # Set to approved instead of pending
        )
        enrollment.save()
        
        messages.success(request, f"You have successfully enrolled in {course.title}!")
        return redirect('student:course_list')
    else:
        form = EnrollmentRequestForm()
    
    context = {
        'form': form,
        'course': course,
    }
    
    return render(request, 'student/enroll_course.html', context)

@login_required
@student_required
def submit_assignment(request, course_id):
    """Submit an assignment for a course"""
    course = get_object_or_404(Course, id=course_id)
    student_profile = request.user.student_profile
    
    # Verify enrollment
    enrollment = get_object_or_404(
        Enrollment, 
        student=student_profile, 
        course=course, 
        status='approved'
    )
    
    # Check if assignment is specified in the URL
    assignment_id = request.GET.get('assignment')
    assignment_title = "Assignment Submission"
    
    if assignment_id:
        try:
            # Get the announcement to pre-fill title
            announcement = Announcement.objects.get(id=assignment_id, course=course)
            if announcement.title.startswith("New Assignment:"):
                assignment_title = f"{announcement.title} - ID:{announcement.id}"
        except Announcement.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.student = student_profile
            assignment.course = course
            
            # If the title wasn't changed, use the pre-filled title
            if not assignment.title or assignment.title == "":
                assignment.title = assignment_title
                
            assignment.save()
            
            messages.success(request, "Assignment submitted successfully!")
            return redirect('student:course_detail', course_id=course.id)
    else:
        form = AssignmentSubmissionForm(initial={'title': assignment_title})
    
    context = {
        'form': form,
        'course': course,
    }
    
    return render(request, 'student/submit_assignment.html', context)

@login_required
@student_required
def assignment_list(request):
    """View all assignments and their status"""
    student_profile = request.user.student_profile
    
    # Get all assignments
    assignments = Assignment.objects.filter(
        student=student_profile
    ).select_related('course').order_by('-submitted_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter == 'graded':
        assignments = assignments.filter(score__isnull=False)
    elif status_filter == 'pending':
        assignments = assignments.filter(score__isnull=True)
    
    # Pagination
    paginator = Paginator(assignments, 10)  # 10 assignments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'student/assignment_list.html', context)

@login_required
@student_required
def profile(request):
    """View and edit student profile"""
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile.objects.create(
            user=request.user,
            registration_number=f"STU{request.user.id}",
            department="Not Specified",
            year_of_study=1
        )
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('student:profile')
    else:
        form = StudentProfileForm(instance=student_profile)
    
    # Get enrollment stats
    enrollment_count = Enrollment.objects.filter(
        student=student_profile, 
        status='approved'
    ).count()
    
    assignment_count = Assignment.objects.filter(
        student=student_profile
    ).count()
    
    completed_assignment_count = Assignment.objects.filter(
        student=student_profile,
        score__isnull=False
    ).count()
    
    context = {
        'form': form,
        'student_profile': student_profile,
        'enrollment_count': enrollment_count,
        'assignment_count': assignment_count,
        'completed_assignment_count': completed_assignment_count,
    }
    
    return render(request, 'student/profile.html', context)

@login_required
@student_required
def view_material(request, material_id):
    """View a specific learning material"""
    material = get_object_or_404(LearningMaterial, id=material_id)
    module = material.module
    course = module.course
    student_profile = request.user.student_profile
    
    # Verify enrollment
    enrollment = get_object_or_404(
        Enrollment, 
        student=student_profile, 
        course=course, 
        status='approved'
    )
    
    context = {
        'material': material,
        'module': module,
        'course': course,
    }
    
    return render(request, 'student/view_material.html', context)

@login_required
@student_required
def view_notifications(request):
    """View all notifications for the student"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        notifications.update(read=True)
    
    # Pagination
    paginator = Paginator(notifications, 15)  # 15 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'student/notifications.html', context)

@login_required
@student_required
def view_submission(request, assignment_id):
    """View a submitted assignment"""
    announcement = get_object_or_404(Announcement, id=assignment_id)
    student_profile = request.user.student_profile
    
    # Find the student's submission for this assignment
    assignment = get_object_or_404(
        Assignment,
        student=student_profile,
        course=announcement.course,
        title__contains=f"ID:{assignment_id}"
    )
    
    context = {
        'announcement': announcement,
        'assignment': assignment,
        'course': announcement.course,
    }
    
    return render(request, 'student/view_submission.html', context)
