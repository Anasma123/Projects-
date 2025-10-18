"""
Extended type hints for Django User model with reverse relations.
This stub file helps Pyright understand dynamically added attributes.
"""

from typing import Any
from django.contrib.auth.models import User as DjangoUser
from django.db.models.manager import RelatedManager

class User(DjangoUser):
    """Extended User model with type hints for reverse relations and annotated fields"""
    id: int
    
    # Reverse relations from ForeignKey
    enrollments: RelatedManager[Any]  # courses.Enrollment
    payments: RelatedManager[Any]  # courses.Payment
    lesson_progress: RelatedManager[Any]  # courses.LessonProgress
    courses_created: RelatedManager[Any]  # courses.Course
    profile: Any  # users.UserProfile
    
    # Annotated fields (added via QuerySet.annotate())
    enrollment_count: int
    total_spent: float | None
