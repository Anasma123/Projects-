from django import forms

from apps.nearride.models import RideCategory
from apps.nearservice.models import ServiceCategory
from apps.nearshop.models import ShopCategory

from .models import PlatformReport


class PlatformReportForm(forms.ModelForm):
    class Meta:
        model = PlatformReport
        fields = ['target_type', 'target_id', 'reason']


class CategoryManageForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'is_active']


class RideCategoryManageForm(forms.ModelForm):
    class Meta:
        model = RideCategory
        fields = ['name', 'description', 'is_active']


class ShopCategoryManageForm(forms.ModelForm):
    class Meta:
        model = ShopCategory
        fields = ['name', 'description', 'is_active']
