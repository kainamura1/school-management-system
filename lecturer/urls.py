from django.urls import path
from . import views

app_name = 'lecturer'

urlpatterns = [
    # Lecturer dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Course management
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/students/', views.student_list, name='student_list'),
    
    # Modules and learning materials
    path('courses/<int:course_id>/modules/', views.manage_modules, name='manage_modules'),
    path('courses/<int:course_id>/modules/create/', views.create_module, name='create_module'),
    path('modules/<int:module_id>/materials/add/', views.add_material, name='add_material'),
    
    # Announcements
    path('courses/<int:course_id>/announcements/create/', views.create_announcement, name='create_announcement'),
    
    # Assignments and grading
    path('courses/<int:course_id>/assignments/', views.manage_assignments, name='manage_assignments'),
    path('assignments/<int:assignment_id>/grade/', views.grade_assignment, name='grade_assignment'),
    path('courses/<int:course_id>/assignments/create/', views.create_assignment, name='create_assignment'),
]
