from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser, StudentProfile, ConsultantProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'role', 'phone', 'country')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define common widget attributes
        widget_attrs = {'class': 'form-control'}
        placeholder_map = {
            'email': 'Email',
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone': 'Phone Number',
            'country': 'Country',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

        # Iterate through the fields available after super().__init__()
        for field_name, field in self.fields.items():
            attrs = widget_attrs.copy()
            if field_name in placeholder_map:
                attrs['placeholder'] = placeholder_map[field_name]
            
            # Apply attributes to the field's widget
            field.widget.attrs.update(attrs)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'country', 'profile_picture', 'bio', 'date_of_birth')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'profile_picture':
                field.widget.attrs.update({'class': 'form-control'})

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('education_level', 'desired_degree', 'desired_major', 'gpa', 
                  'language_test_type', 'language_score', 'work_experience', 'resume')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'resume':
                field.widget.attrs.update({'class': 'form-control'})

class ConsultantProfileForm(forms.ModelForm):
    class Meta:
        model = ConsultantProfile
        fields = ('specialization', 'years_of_experience', 'available_for_appointment')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'available_for_appointment':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
