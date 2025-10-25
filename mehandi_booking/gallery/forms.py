from django import forms
from .models import Category, SubCategory, Design

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check for case-insensitive duplicates, excluding the current instance when editing
            queryset = Category.objects.filter(name__iexact=name)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("A category with that name already exists (case-insensitive).")
        return name

class SubCategoryForm(forms.ModelForm):
    SUBCATEGORY_CHOICES = [
        ('one hand', 'One Hand'),
        ('two hand', 'Two Hand'),
        ('full hand', 'Full Hand'),
    ]
    
    name = forms.ChoiceField(choices=SUBCATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data:
            category = cleaned_data.get('category')
            name = cleaned_data.get('name')
            
            if category and name:
                # Check for case-insensitive duplicates within the same category, excluding the current instance when editing
                queryset = SubCategory.objects.filter(category=category, name__iexact=name)
                if self.instance.pk:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if queryset.exists():
                    raise forms.ValidationError("A sub-category with that name already exists in this category (case-insensitive).")
        
        return cleaned_data

class DesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ['category', 'sub_category', 'name', 'image', 'optional_image', 'description', 'price']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'sub_category': forms.Select(attrs={'class': 'form-control', 'id': 'id_sub_category'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'optional_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_price'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        category = self.cleaned_data.get('category')
        
        if name and category:
            # Check for case-insensitive duplicates within the same category, excluding the current instance when editing
            queryset = Design.objects.filter(category=category, name__iexact=name)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("A design with that name already exists in this category (case-insensitive).")
        return name