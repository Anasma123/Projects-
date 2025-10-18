from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment, Payment, LessonProgress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'price', 'is_free', 'is_published', 'created_at']
    list_filter = ['is_free', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)} if hasattr(Course, 'slug') else {}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'description']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'order']
    list_filter = ['lesson_type', 'module__course']
    search_fields = ['title', 'content']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'completed', 'progress']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['user__username', 'course__title']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'course__title', 'order_id', 'payment_id']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at', 'time_spent']
    list_filter = ['completed', 'completed_at', 'lesson__module__course']
    search_fields = ['user__username', 'lesson__title']
