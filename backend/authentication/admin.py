from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LoginSession, AccessCodeHistory

# Si le CustomUser n'est pas encore enregistré, on ignore l'erreur
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

# --- CustomUserAdmin unique ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Colonnes affichées dans la liste
    list_display = ['username', 'is_active', 'last_login', 'poste']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['username']

    # Fieldsets pour modification
    fieldsets = (
        (None, {'fields': ('username', 'password', 'code_acces')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
        ('Informations professionnelles', {'fields': ('department', 'site', 'poste')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'last_code_change')}),
    )

    # Fieldsets pour ajout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'code_acces', 'email', 'department', 'site', 'poste', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )

# --- Autres modèles ---
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
