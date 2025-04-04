from django.db import models
from django.utils.text import slugify

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    flag = models.ImageField(upload_to='flags/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Countries'

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"
    
    class Meta:
        verbose_name_plural = 'Cities'

class University(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='university_banners/', blank=True, null=True)
    description = models.TextField()
    established_year = models.PositiveIntegerField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='universities')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='universities')
    ranking = models.PositiveIntegerField(blank=True, null=True, help_text="Global ranking")
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    student_population = models.PositiveIntegerField(blank=True, null=True)
    international_students = models.PositiveIntegerField(blank=True, null=True)
    fee_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Approximate annual fee in USD")
    intake_details = models.TextField(blank=True, null=True, help_text="Information about application intakes (e.g., Fall, Spring, Rolling)")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Universities'

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties')
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.university.name}"
    
    class Meta:
        verbose_name_plural = 'Faculties'

class Program(models.Model):
    BACHELOR = 'bachelor'
    MASTER = 'master'
    PHD = 'phd'
    DIPLOMA = 'diploma'
    CERTIFICATE = 'certificate'
    
    DEGREE_TYPES = [
        (BACHELOR, 'Bachelor\'s Degree'),
        (MASTER, 'Master\'s Degree'),
        (PHD, 'PhD/Doctorate'),
        (DIPLOMA, 'Diploma'),
        (CERTIFICATE, 'Certificate'),
    ]
    
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    ONLINE = 'online'
    HYBRID = 'hybrid'
    
    STUDY_MODES = [
        (FULL_TIME, 'Full-Time'),
        (PART_TIME, 'Part-Time'),
        (ONLINE, 'Online'),
        (HYBRID, 'Hybrid'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='programs')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='programs')
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    study_mode = models.CharField(max_length=20, choices=STUDY_MODES, default=FULL_TIME)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in months")
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    fee_currency = models.CharField(max_length=3, default='USD')
    language = models.CharField(max_length=50, default='English')
    entry_requirements = models.TextField(blank=True, null=True)
    application_deadline = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    scholarship_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.university.name}-{self.name}-{self.degree_type}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_degree_type_display()}) - {self.university.name}"

class ProgramRequirement(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='requirements')
    name = models.CharField(max_length=100)
    description = models.TextField()
    minimum_score = models.CharField(max_length=100, blank=True, null=True)
    is_mandatory = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} for {self.program.name}"
