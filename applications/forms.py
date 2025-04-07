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
    # Add the new required document fields
    cv_file = forms.FileField(label="CV/Resume", required=True)
    recommendation_letter_file = forms.FileField(label="Recommendation Letter", required=True)
    statement_of_purpose_file = forms.FileField(label="Statement of Purpose", required=True)


    class Meta:
        model = Application
        # Include fields from the model + custom fields if needed
        fields = [
            # Personal Info
            'email_address',
            'birthdate',
            'country',
            'street_address',
            'city',
            'postal_code',
            'mailing_address',
            'telephone_primary',
            'telephone_secondary',
            # Existing fields
            'intake_date',
            'gpa_or_percentage',
            'study_gap_years',
            'ielts_score',
            'duolingo_score',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'notes'
            # Document fields are handled by the form class itself, not the model Meta
        ]
        widgets = {
            # Personal Info Widgets
            'email_address': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Nepal'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 123 Main St'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kathmandu'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 44600'}),
            'mailing_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter if different from street address'}),
            'telephone_primary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +977 98XXXXXXXX'}),
            'telephone_secondary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            # Existing Widgets
            'intake_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gpa_or_percentage': forms.TextInput(attrs={'placeholder': 'e.g., 3.8 GPA or 85%', 'class': 'form-control'}),
            'study_gap_years': forms.NumberInput(attrs={'placeholder': 'Years', 'class': 'form-control'}),
            'ielts_score': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'e.g., 7.5', 'class': 'form-control'}),
            'duolingo_score': forms.NumberInput(attrs={'placeholder': 'e.g., 120', 'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add any additional information...', 'class': 'form-control'}),
            # Document Widgets (already defined in the form class, but added here for completeness if needed)
            'transcript_file': forms.FileInput(attrs={'class': 'form-control'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
            'passport_file': forms.FileInput(attrs={'class': 'form-control'}),
            'language_test_file': forms.FileInput(attrs={'class': 'form-control'}),
            'cv_file': forms.FileInput(attrs={'class': 'form-control'}),
            'recommendation_letter_file': forms.FileInput(attrs={'class': 'form-control'}),
            'statement_of_purpose_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            # Personal Info Labels
            'email_address': 'Email Address',
            'birthdate': 'Date of Birth',
            'country': 'Country',
            'street_address': 'Street Address',
            'city': 'City',
            'postal_code': 'Postal Code',
            'mailing_address': 'Mailing Address (if different)',
            'telephone_primary': 'Primary Telephone',
            'telephone_secondary': 'Secondary Telephone (Optional)',
            # Existing Labels
            'gpa_or_percentage': 'GPA / Percentage',
            'study_gap_years': 'Study Gap (Years)',
            'ielts_score': 'IELTS Score (if applicable)',
            'duolingo_score': 'Duolingo Score (if applicable)',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
            'emergency_contact_relationship': 'Emergency Contact Relationship',
            'notes': 'Additional Notes',
        }
