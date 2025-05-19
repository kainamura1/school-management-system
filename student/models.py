from django.db import models
from accounts.models import User
from course.models import Course

class StudentProfile(models.Model):
    """Student profile model extending the user model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    year_of_study = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.registration_number}"

class Enrollment(models.Model):
    """Model for student course enrollments"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ('student', 'course')
        
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}"

class Assignment(models.Model):
    """Model for student assignments"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    submission = models.FileField(upload_to='assignments/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.student.user.username}"
