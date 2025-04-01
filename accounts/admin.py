from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, ConsultantProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'

class ConsultantProfileInline(admin.StackedInline):
    model = ConsultantProfile
    can_delete = False
    verbose_name_plural = 'Consultant Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone', 'country', 'profile_picture', 'bio')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == CustomUser.STUDENT:
                return [StudentProfileInline]
            elif obj.role == CustomUser.CONSULTANT:
                return [ConsultantProfileInline]
        return []

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(ConsultantProfile)
