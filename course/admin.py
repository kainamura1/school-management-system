from django.contrib import admin
from .models import Course, CourseModule, LearningMaterial

class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    show_change_link = True
    fields = ('title', 'order', 'description')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'credits', 'is_active', 'enrolled_students_count')
    list_filter = ('is_active', 'created_at', 'credits')
    search_fields = ('code', 'title', 'description')
    date_hierarchy = 'created_at'
    inlines = [CourseModuleInline]
    
    def enrolled_students_count(self, obj):
        return obj.enrollments.filter(status='approved').count()
    enrolled_students_count.short_description = 'Students'
    
    fieldsets = (
        ('Course Information', {
            'fields': ('code', 'title', 'description', 'credits')
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )

class LearningMaterialInline(admin.TabularInline):
    model = LearningMaterial
    extra = 1
    fields = ('title', 'file', 'description')

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'materials_count')
    list_filter = ('course',)
    search_fields = ('title', 'description', 'course__code', 'course__title')
    inlines = [LearningMaterialInline]
    
    def materials_count(self, obj):
        return obj.materials.count()
    materials_count.short_description = 'Materials'
    
    fieldsets = (
        ('Module Information', {
            'fields': ('course', 'title', 'description', 'order')
        }),
    )

@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'module_course_display', 'upload_date', 'file_type')
    list_filter = ('upload_date', 'module__course')
    search_fields = ('title', 'description', 'module__title')
    date_hierarchy = 'upload_date'
    
    def module_course_display(self, obj):
        return f"{obj.module.course.code} - {obj.module.title}"
    module_course_display.short_description = 'Course Module'
    
    def file_type(self, obj):
        if obj.file:
            filename = obj.file.name.lower()
            if filename.endswith(('.pdf')):
                return "PDF"
            elif filename.endswith(('.doc', '.docx')):
                return "Word"
            elif filename.endswith(('.ppt', '.pptx')):
                return "PowerPoint"
            elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return "Image"
            elif filename.endswith(('.mp4', '.avi', '.mov')):
                return "Video"
            else:
                return filename.split('.')[-1].upper()
        return "None"
    file_type.short_description = 'Type'
    
    fieldsets = (
        ('Material Information', {
            'fields': ('title', 'description', 'module')
        }),
        ('File', {
            'fields': ('file',)
        }),
    )
