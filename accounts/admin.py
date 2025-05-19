from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {'fields': ('user_type', 'profile_picture', 'date_of_birth', 'phone_number', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Information', {'fields': ('user_type', 'profile_picture', 'date_of_birth', 'phone_number', 'address')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    actions = ['make_lecturer', 'make_student']
    
    def make_lecturer(self, request, queryset):
        # Update user role to lecturer
        updated = queryset.update(user_type='lecturer')
        self.message_user(request, f"{updated} users were successfully changed to lecturer role.")
    make_lecturer.short_description = "Change selected users to lecturer role"
    
    def make_student(self, request, queryset):
        # Update user role to student
        updated = queryset.update(user_type='student')
        self.message_user(request, f"{updated} users were successfully changed to student role.")
    make_student.short_description = "Change selected users to student role"

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Notification, NotificationAdmin)
