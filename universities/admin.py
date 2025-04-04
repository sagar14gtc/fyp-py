from django.contrib import admin
from .models import Country, City, University, Faculty, Program, ProgramRequirement

class CityInline(admin.TabularInline):
    model = City
    extra = 1

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    inlines = [CityInline]

class FacultyInline(admin.TabularInline):
    model = Faculty
    extra = 1

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'ranking', 'is_featured')
    list_filter = ('country', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    # Add the new fields to the list display
    list_display = ('name', 'country', 'city', 'ranking', 'fee_usd', 'is_featured')
    # Add the new fields to the form fields for editing
    fields = ('name', 'slug', 'logo', 'banner_image', 'description', 'established_year',
              'website', 'email', 'phone', 'address', 'city', 'country', 'ranking',
              'acceptance_rate', 'student_population', 'international_students',
              'fee_usd', 'intake_details', 'is_featured')
    inlines = [FacultyInline]

class ProgramRequirementInline(admin.TabularInline):
    model = ProgramRequirement
    extra = 1

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'faculty', 'degree_type', 'study_mode', 'duration', 'tuition_fee', 'start_date') # Added start_date
    list_filter = ('degree_type', 'study_mode', 'university', 'scholarship_available', 'start_date') # Added start_date filter
    search_fields = ('name', 'description', 'university__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProgramRequirementInline]

admin.site.register(Country, CountryAdmin)
admin.site.register(City)
admin.site.register(University, UniversityAdmin)
admin.site.register(Faculty)
admin.site.register(Program, ProgramAdmin)
admin.site.register(ProgramRequirement)
