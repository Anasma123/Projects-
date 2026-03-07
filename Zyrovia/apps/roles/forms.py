from django import forms

from .models import RoleChoices


class RoleAssignmentForm(forms.Form):
    role = forms.ChoiceField(choices=RoleChoices.choices)
