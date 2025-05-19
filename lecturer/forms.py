from django import forms
from django.utils import timezone
from .models import Announcement
from course.models import Course, CourseModule, LearningMaterial
from student.models import Assignment

class CourseForm(forms.ModelForm):
    """Form for creating and editing courses"""
    class Meta:
        model = Course
        fields = ['code', 'title', 'description', 'credits', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS101'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Introduction to Computer Science'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            return code
            
        # Check if code exists (for new courses)
        if not self.instance.pk and Course.objects.filter(code=code).exists():
            raise forms.ValidationError("This course code already exists.")
        return code


class CourseModuleForm(forms.ModelForm):
    """Form for creating and editing course modules"""
    order = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        help_text="Module order number"
    )
    
    class Meta:
        model = CourseModule
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Module 1: Introduction'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LearningMaterialForm(forms.ModelForm):
    """Form for adding learning materials to modules"""
    class Meta:
        model = LearningMaterial
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Lecture Slides'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Limit file size to 50MB
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 50MB")
                
            # Check file extension to ensure it's a common document/media type
            allowed_extensions = [
                'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
                'txt', 'csv', 'mp4', 'mp3', 'zip', 'rar', 'jpg', 'jpeg', 
                'png', 'gif'
            ]
            
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
                )
        return file


class AnnouncementForm(forms.ModelForm):
    """Form for creating announcements for a course"""
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Limit file size to 10MB
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")
                
            # Check file extension
            allowed_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'zip', 'jpg', 'jpeg', 'png']
            file_extension = attachment.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
                )
        return attachment


class AssignmentGradingForm(forms.ModelForm):
    """Form for grading student assignments"""
    class Meta:
        model = Assignment
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 100, 
                'step': 0.1
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Provide constructive feedback to the student'
            }),
        }
    
    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is not None:
            if score < 0 or score > 100:
                raise forms.ValidationError("Score must be between 0 and 100")
        return score


class AssignmentCreationForm(forms.ModelForm):
    """Form for creating new assignments"""
    class Meta:
        model = Assignment
        fields = ['title', 'submission']  # Use only fields that exist in the model
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment Title'}),
            'submission': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    # Add any additional fields as form-only fields (not model fields)
    instructions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Instructions and requirements'
        }),
        required=False
    )
