from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    # User Roles
    STUDENT = 'student'
    CONSULTANT = 'consultant'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, _('Student')),
        (CONSULTANT, _('Consultant')),
        (ADMIN, _('Administrator')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
        
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    education_level = models.CharField(max_length=100, blank=True, null=True)
    desired_degree = models.CharField(max_length=100, blank=True, null=True)
    desired_major = models.CharField(max_length=100, blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    language_test_type = models.CharField(max_length=50, blank=True, null=True)  # IELTS, TOEFL, etc.
    language_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    work_experience = models.PositiveIntegerField(default=0, help_text="Experience in years")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"

class ConsultantProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='consultant_profile')
    specialization = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    available_for_appointment = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email}'s Consultant Profile"
