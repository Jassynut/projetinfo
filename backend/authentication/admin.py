# authentication/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LoginSession, AccessCodeHistory

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'departement', 'site', 'is_active', 'last_login']
    list_filter = ['departement', 'site', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'matricule']
    ordering = ['last_name', 'first_name']
    
    fieldsets = (
        (None, {'fields': ('username', 'code_acces')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
        ('Informations professionnelles', {'fields': ('departement', 'site', 'poste', 'matricule')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'last_code_change')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'code_acces', 'first_name', 'last_name', 'departement', 'site', 'is_staff', 'is_active'),
        }),
    )

@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'ip_address', 'success', 'failure_reason']
    list_filter = ['success', 'login_time']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['user', 'login_time', 'ip_address', 'user_agent', 'success', 'failure_reason']

@admin.register(AccessCodeHistory)
class AccessCodeHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'changed_at', 'changed_by']
    list_filter = ['changed_at']
    search_fields = ['user__username']
    readonly_fields = ['user', 'old_code', 'new_code', 'changed_at', 'changed_by']