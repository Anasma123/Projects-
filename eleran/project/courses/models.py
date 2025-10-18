from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Course(models.Model):
    """Model for storing course information"""
    objects = models.Manager()  # Explicit manager declaration for type checkers
    
    # Explicit type hints for auto-generated and reverse relations
    if TYPE_CHECKING:
        id: int
        modules: 'RelatedManager[Module]'
        enrollments: 'RelatedManager[Enrollment]'
        payments: 'RelatedManager[Payment]'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Module(models.Model):
    """Model for course modules/sections"""
    objects = models.Manager()  # Explicit manager declaration for type checkers
    
    # Explicit type hints for auto-generated and reverse relations
    if TYPE_CHECKING:
        id: int
        lessons: 'RelatedManager[Lesson]'
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Model for individual lessons within modules"""
    objects = models.Manager()  # Explicit manager declaration for type checkers
    
    # Explicit type hints for auto-generated and reverse relations
    if TYPE_CHECKING:
        id: int
        user_progress: 'RelatedManager[LessonProgress]'
    
    VIDEO = 'video'
    TEXT = 'text'
    RESOURCE = 'resource'
    
    LESSON_TYPES = [
        (VIDEO, 'Video'),
        (TEXT, 'Text'),
        (RESOURCE, 'Resource'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default=TEXT)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True, help_text='YouTube URL or video link')
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    resource_file = models.FileField(upload_to='lesson_resources/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.DurationField(blank=True, null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Enrollment(models.Model):
    """Model for tracking user enrollments in courses"""
    objects = models.Manager()  # Explicit manager declaration for type checkers
    
    # Explicit type hints for auto-generated fields
    if TYPE_CHECKING:
        id: int
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)
    progress = models.PositiveIntegerField(default=0)  # Percentage 0-100
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class Payment(models.Model):
    """Model for tracking payments"""
    objects = models.Manager()  # Explicit manager declaration for type checkers
    
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True)
    order_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.status}"


class LessonProgress(models.Model):
    """Model for tracking user progress on individual lessons"""
    objects = models.Manager()  # Explicit manager declaration for type checkers
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True, help_text='Time spent on this lesson')
    
    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['lesson__order']
        verbose_name_plural = 'Lesson Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'Completed' if self.completed else 'In Progress'}"
