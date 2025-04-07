from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from universities.models import Program
import uuid

class Application(models.Model):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    PROCESSING = 'processing'
    DOCUMENTS_REQUIRED = 'documents_required'
    UNDER_REVIEW = 'under_review'
    CONDITIONALLY_ACCEPTED = 'conditionally_accepted'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    DEFERRED = 'deferred'
    WAITLISTED = 'waitlisted'
    VISA_APPLIED = 'visa_applied'
    VISA_APPROVED = 'visa_approved'
    VISA_REJECTED = 'visa_rejected'
    ENROLLMENT_CONFIRMED = 'enrollment_confirmed'
    CANCELED = 'canceled'

    STATUS_CHOICES = [
        (DRAFT, _('Draft')),
        (SUBMITTED, _('Submitted')),
        (PROCESSING, _('Processing')),
        (DOCUMENTS_REQUIRED, _('Documents Required')),
        (UNDER_REVIEW, _('Under Review')),
        (CONDITIONALLY_ACCEPTED, _('Conditionally Accepted')),
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (DEFERRED, _('Deferred')),
        (WAITLISTED, _('Waitlisted')),
        (VISA_APPLIED, _('Visa Applied')),
        (VISA_APPROVED, _('Visa Approved')),
        (VISA_REJECTED, _('Visa Rejected')),
        (ENROLLMENT_CONFIRMED, _('Enrollment Confirmed')),
        (CANCELED, _('Canceled')),
    ]

    application_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications', limit_choices_to={'role': 'student'})
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications')
    consultant = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_applications', limit_choices_to={'role': 'consultant'})
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=DRAFT)
    intake_date = models.DateField(help_text=_("Expected start date for the program"))
    application_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Personal Information Section
    email_address = models.EmailField(max_length=254, blank=True, null=True, help_text=_("Contact email for this application")) # Assuming separate from user account email
    birthdate = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    mailing_address = models.TextField(blank=True, null=True, help_text=_("If different from street address"))
    telephone_primary = models.CharField(max_length=20, blank=True, null=True)
    telephone_secondary = models.CharField(max_length=20, blank=True, null=True)

    # Additional student-provided info
    gpa_or_percentage = models.CharField(max_length=10, blank=True, null=True, help_text=_("e.g., 3.8 GPA or 85%"))
    study_gap_years = models.PositiveIntegerField(blank=True, null=True, help_text=_("Number of years gap in studies, if any"))
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    ielts_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    duolingo_score = models.PositiveIntegerField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True) # General notes field

    def __str__(self):
        return f"APP-{self.application_id}"

    class Meta:
        ordering = ['-application_date']

class Document(models.Model):
    TRANSCRIPT = 'transcript'
    DIPLOMA = 'diploma'
    CV = 'cv'
    RECOMMENDATION_LETTER = 'recommendation_letter'
    PASSPORT = 'passport'
    LANGUAGE_TEST = 'language_test'
    STATEMENT_OF_PURPOSE = 'statement_of_purpose'
    PORTFOLIO = 'portfolio'
    OTHER = 'other'

    DOCUMENT_TYPES = [
        (TRANSCRIPT, _('Academic Transcript')),
        (DIPLOMA, _('Diploma/Degree Certificate')),
        (CV, _('CV/Resume')),
        (RECOMMENDATION_LETTER, _('Recommendation Letter')),
        (PASSPORT, _('Passport')),
        (LANGUAGE_TEST, _('Language Test Score')),
        (STATEMENT_OF_PURPOSE, _('Statement of Purpose')),
        (PORTFOLIO, _('Portfolio')),
        (OTHER, _('Other')),
    ]

    NOT_UPLOADED = 'not_uploaded'
    PENDING_REVIEW = 'pending_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (NOT_UPLOADED, _('Not Uploaded')),
        (PENDING_REVIEW, _('Pending Review')),
        (APPROVED, _('Approved')),
        (REJECTED, _('Rejected')),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='application_documents/', blank=True, null=True)
    name = models.CharField(max_length=255) # Consider making this optional or auto-generated
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NOT_UPLOADED)
    required = models.BooleanField(default=True) # We might adjust this later based on program requirements
    feedback = models.TextField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.application}"

class ApplicationNote(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='application_notes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.user.username} on {self.application}"

    class Meta:
        ordering = ['-created_at']

class ApplicationStatus(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.application} - {self.get_status_display()}"

    class Meta:
        verbose_name_plural = 'Application Statuses'
        ordering = ['-changed_at']
