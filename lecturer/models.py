from django.db import models
from accounts.models import User
from course.models import Course

class LecturerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    office_number = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.staff_id}"

class LecturerCourse(models.Model):
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lecturers')
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('lecturer', 'course')
        
    def __str__(self):
        return f"{self.lecturer.user.username} - {self.course.title}"

class Announcement(models.Model):
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE, related_name='announcements')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='announcements/', null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-posted_at']
