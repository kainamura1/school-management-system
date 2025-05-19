from django.contrib import admin
from .models import LecturerProfile, LecturerCourse, Announcement

@admin.register(LecturerProfile)
class LecturerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'department', 'specialization')
    search_fields = ('user__username', 'user__email', 'staff_id', 'department')
    list_filter = ('department',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('staff_id', 'department', 'specialization', 'office_number')
        }),
    )

@admin.register(LecturerCourse)
class LecturerCourseAdmin(admin.ModelAdmin):
    list_display = ('lecturer', 'course', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('lecturer__user__username', 'course__title', 'course__code')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lecturer__user', 'course')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'lecturer', 'course', 'posted_at', 'has_attachment')
    list_filter = ('posted_at', 'course')
    search_fields = ('title', 'content', 'lecturer__user__username', 'course__title')
    date_hierarchy = 'posted_at'
    
    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = 'Has Attachment'
    
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'content', 'attachment')
        }),
        ('Related Information', {
            'fields': ('lecturer', 'course')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lecturer__user', 'course')
