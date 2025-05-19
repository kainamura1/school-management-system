from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Course-related URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/submit-assignment/', views.submit_assignment, name='submit_assignment'),
    path('submissions/<int:assignment_id>/', views.view_submission, name='view_submission'),
    
    # Assignments
    path('assignments/', views.assignment_list, name='assignment_list'),
    
    # Learning materials
    path('materials/<int:material_id>/', views.view_material, name='view_material'),
    
    # Notifications
    path('notifications/', views.view_notifications, name='view_notifications'),
]
