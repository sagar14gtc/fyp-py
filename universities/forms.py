from django import forms
from .models import University, Country, City

class UniversityForm(forms.ModelForm):
    """Form for adding/editing Universities."""

    # Allow creating new City/Country if needed, or use existing ones
    # This requires more complex handling, maybe using django-select2 or similar.
    # For simplicity now, we'll use ModelChoiceFields.
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(), # Consider filtering by country dynamically if possible
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = University
        fields = [
            'name', 'description', 'website', 'country', 'city',
            'address', 'ranking', 'logo', 'banner_image', 'fee_usd', 'intake_details', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'ranking': forms.NumberInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'banner_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fee_usd': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'intake_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # Add clean methods or __init__ for dynamic filtering (e.g., city based on country) if needed
