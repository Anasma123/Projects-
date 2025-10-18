from typing import TYPE_CHECKING, Any
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

# Add type hints for User model's reverse relations and dynamic attributes
if TYPE_CHECKING:
    # Extend User model with type hints for reverse relations
    class ExtendedUser(User):
        id: int
        enrollments: 'RelatedManager[Any]'  # courses.Enrollment
        payments: 'RelatedManager[Any]'  # courses.Payment
        lesson_progress: 'RelatedManager[Any]'  # courses.LessonProgress
        courses_created: 'RelatedManager[Any]'  # courses.Course
        profile: 'UserProfile'
        # Annotated fields (added dynamically via QuerySet.annotate())
        enrollment_count: int
        total_spent: float


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    instance.profile.save()
