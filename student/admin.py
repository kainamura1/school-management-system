from django.contrib import admin
from .models import StudentProfile, Enrollment, Assignment

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'user', 'department', 'year_of_study')
    list_filter = ('department', 'year_of_study')
    search_fields = ('user__username', 'user__email', 'registration_number', 'department')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('registration_number', 'department', 'year_of_study')
        }),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrollment_date')
    list_filter = ('status', 'enrollment_date', 'course')
    search_fields = ('student__user__username', 'student__registration_number', 'course__title', 'course__code')
    date_hierarchy = 'enrollment_date'
    
    actions = ['approve_enrollments', 'reject_enrollments']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'course')
    
    def approve_enrollments(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} enrollment(s) successfully approved.")
    approve_enrollments.short_description = "Approve selected enrollments"
    
    def reject_enrollments(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} enrollment(s) rejected.")
    reject_enrollments.short_description = "Reject selected enrollments"

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'course', 'submitted_at', 'score', 'graded_status')
    list_filter = ('submitted_at', 'course')
    search_fields = ('title', 'student__user__username', 'student__registration_number', 'course__title')
    date_hierarchy = 'submitted_at'
    
    readonly_fields = ('submission', 'submitted_at')
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('title', 'submission', 'submitted_at')
        }),
        ('Academic Information', {
            'fields': ('student', 'course')
        }),
        ('Grading', {
            'fields': ('score', 'feedback'),
            'classes': ('wide',)
        }),
    )
    
    def graded_status(self, obj):
        return "Graded" if obj.score is not None else "Pending"
    graded_status.short_description = "Status"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'course')
