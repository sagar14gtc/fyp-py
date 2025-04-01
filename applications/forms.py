from django import forms
from .models import Application, Document, ApplicationNote

class ApplicationForm(forms.ModelForm):
    """Form for creating and editing applications."""
    
    class Meta:
        model = Application
        fields = ['intake_date', 'notes']
        widgets = {
            'intake_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add any additional information about your application here...'}),
        }

class DocumentForm(forms.ModelForm):
    """Form for uploading application documents."""
    
    class Meta:
        model = Document
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ApplicationNoteForm(forms.ModelForm):
    """Form for adding notes to applications."""
    
    class Meta:
        model = ApplicationNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your note here...', 'class': 'form-control'}),
        }

class ApplicationCreateFromSearchForm(forms.ModelForm):
    """Form for creating application from search results, including extra fields."""
    
    # Add fields for document uploads directly in this form for simplicity
    # In a real-world scenario, you might handle documents separately after initial application creation
    transcript_file = forms.FileField(label="Academic Transcript", required=True)
    certificate_file = forms.FileField(label="Diploma/Degree Certificate", required=True)
    passport_file = forms.FileField(label="Passport Copy", required=True)
    language_test_file = forms.FileField(label="Language Test Score Document", required=False)

    class Meta:
        model = Application
        # Include fields from the model + custom fields if needed
        fields = [
            'intake_date', 
            'gpa_or_percentage', 
            'study_gap_years',
            'ielts_score',
            'duolingo_score',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'notes',
            # Add document fields here
            'transcript_file', 
            'certificate_file', 
            'passport_file', 
            'language_test_file'
        ]
        widgets = {
            'intake_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gpa_or_percentage': forms.TextInput(attrs={'placeholder': 'e.g., 3.8 GPA or 85%', 'class': 'form-control'}),
            'study_gap_years': forms.NumberInput(attrs={'placeholder': 'Years', 'class': 'form-control'}),
            'ielts_score': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'e.g., 7.5', 'class': 'form-control'}),
            'duolingo_score': forms.NumberInput(attrs={'placeholder': 'e.g., 120', 'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add any additional information...', 'class': 'form-control'}),
            'transcript_file': forms.FileInput(attrs={'class': 'form-control'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
            'passport_file': forms.FileInput(attrs={'class': 'form-control'}),
            'language_test_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'gpa_or_percentage': 'GPA / Percentage',
            'study_gap_years': 'Study Gap (Years)',
            'ielts_score': 'IELTS Score (if applicable)',
            'duolingo_score': 'Duolingo Score (if applicable)',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
            'emergency_contact_relationship': 'Emergency Contact Relationship',
            'notes': 'Additional Notes',
        }
