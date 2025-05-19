from django.db import models

# Create your models here.

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.title}"

class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
        
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class LearningMaterial(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='learning_materials/')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
