from django import forms
from .models import StudentProfile, Assignment, Enrollment

class AssignmentSubmissionForm(forms.ModelForm):
    """Form for students to submit assignments"""
    class Meta:
        model = Assignment
        fields = ['title', 'submission']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment Title'}),
            'submission': forms.FileInput(attrs={'class': 'form-control'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = "Enter a descriptive title for your assignment submission."
        self.fields['submission'].help_text = "Upload your assignment file. Accepted formats: PDF, DOC, DOCX, PPTX, ZIP (Max size: 10MB)"
        
    def clean_submission(self):
        """Validate the submitted file"""
        submission = self.cleaned_data.get('submission')
        if submission:
            # Check file size (10MB limit)
            if submission.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")
                
            # Check file extension
            allowed_extensions = ['pdf', 'doc', 'docx', 'pptx', 'zip']
            file_extension = submission.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}")
        
        return submission


class EnrollmentRequestForm(forms.Form):
    """Form for students to request enrollment in a course"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Optional: Include a message with your enrollment request."
    )
    
    terms_agreement = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I agree to follow the course guidelines and complete all required assignments."
    )


class StudentProfileForm(forms.ModelForm):
    """Form for students to update their profile information"""
    class Meta:
        model = StudentProfile
        fields = ['department', 'year_of_study']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 7}),
        }
        
    def clean_year_of_study(self):
        """Validate year of study"""
        try:
            year = self.cleaned_data.get('year_of_study')
            if year is None:
                return 1  # Default to year 1 if not provided
                
            # Ensure it's an integer
            year = int(year)
            
            # Validate range
            if year < 1 or year > 7:
                raise forms.ValidationError("Year of study must be between 1 and 7")
                
            return year
        except (ValueError, TypeError):
            # Handle case where the input isn't convertible to an integer
            raise forms.ValidationError("Please enter a valid year as a number between 1 and 7")
