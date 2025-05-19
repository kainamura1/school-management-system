from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Course, CourseModule

def course_list(request):
    """Display all active courses"""
    courses = Course.objects.filter(is_active=True).order_by('code')
    
    # Pagination
    paginator = Paginator(courses, 12)  # Show 12 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'courses_count': courses.count(),
    }
    
    return render(request, 'course/course_list.html', context)

def course_detail(request, course_id):
    """Display details of a specific course"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    modules = CourseModule.objects.filter(course=course).order_by('order')
    
    # Check if the user is enrolled (for students) or teaching (for lecturers)
    user_enrolled = False
    user_teaching = False
    
    if request.user.is_authenticated:
        if request.user.user_type == 'student':
            try:
                from student.models import Enrollment
                user_enrolled = Enrollment.objects.filter(
                    student__user=request.user,
                    course=course,
                    status='approved'
                ).exists()
            except:
                pass
        elif request.user.user_type == 'lecturer':
            try:
                from lecturer.models import LecturerCourse
                user_teaching = LecturerCourse.objects.filter(
                    lecturer__user=request.user,
                    course=course
                ).exists()
            except:
                pass
    
    context = {
        'course': course,
        'modules': modules,
        'user_enrolled': user_enrolled,
        'user_teaching': user_teaching,
    }
    
    return render(request, 'course/course_detail.html', context)

def course_search(request):
    """Search for courses by various criteria"""
    query = request.GET.get('q', '')
    
    if query:
        courses = Course.objects.filter(
            Q(is_active=True) &
            (Q(title__icontains=query) | 
             Q(code__icontains=query) | 
             Q(description__icontains=query))
        ).order_by('code')
    else:
        courses = Course.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Pagination
    paginator = Paginator(courses, 12)  # Show 12 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'courses_count': courses.count(),
    }
    
    return render(request, 'course/course_search.html', context)
