# authentication/admin.py - CORRESPONDANT À TES AUTRES FICHIERS
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import TestUser


class TestUserAdmin(UserAdmin):
    """Interface d'administration pour TestUser"""
    
    # Affichage dans la liste - AVEC LES MÉTHODES *_display
    list_display = (
        'cin_display', 
        'username_display', 
        'full_name_display', 
        'email_display',
        'is_active_display', 
        'is_staff_display',
        'date_joined_display',
    )
    
    # Filtres
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    # Champs de recherche
    search_fields = ('cin', 'username', 'full_name', 'email')
    
    # Organisation dans le formulaire d'édition
    fieldsets = (
        ('Informations de connexion', {'fields': ('cin', 'username', 'password')}),
        ('Informations personnelles', {'fields': ('full_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )
    
    # Organisation dans le formulaire de création
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cin', 'username', 'full_name', 'email', 'password1', 'password2'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    
    # Tri par défaut
    ordering = ('-date_joined', 'cin')
    
    # Actions personnalisées
    actions = ['activate_users', 'deactivate_users', 'make_staff', 'remove_staff']
    
    # Configuration des colonnes
    list_display_links = ('cin_display', 'username_display')
    list_per_page = 50
    
    # ==================== MÉTHODES D'AFFICHAGE (CELLES QUI MANQUAIENT) ====================
    
    def cin_display(self, obj):
        """Affiche le CIN avec un badge"""
        return format_html('<span style="font-weight: bold; color: #1976d2;">{}</span>', obj.cin)
    cin_display.short_description = 'CIN'
    cin_display.admin_order_field = 'cin'
    
    def username_display(self, obj):
        """Affiche le username"""
        return format_html('<code>{}</code>', obj.username)
    username_display.short_description = 'Username'
    username_display.admin_order_field = 'username'
    
    def full_name_display(self, obj):
        """Affiche le nom complet"""
        if obj.full_name:
            return obj.full_name
        return format_html('<span style="color: #999; font-style: italic;">Non renseigné</span>')
    full_name_display.short_description = 'Nom complet'
    full_name_display.admin_order_field = 'full_name'
    
    def email_display(self, obj):
        """Affiche l'email"""
        if obj.email:
            return obj.email
        return format_html('<span style="color: #999; font-style: italic;">-</span>')
    email_display.short_description = 'Email'
    email_display.admin_order_field = 'email'
    
    def is_active_display(self, obj):
        """Affiche l'état actif/inactif avec des couleurs"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Actif</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactif</span>')
    is_active_display.short_description = 'Statut'
    is_active_display.admin_order_field = 'is_active'
    
    def is_staff_display(self, obj):
        """Affiche si c'est un staff"""
        if obj.is_staff:
            return format_html('<span style="color: #ff9800; font-weight: bold;">👨‍💼 Staff</span>')
        return format_html('<span style="color: #666;">Utilisateur</span>')
    is_staff_display.short_description = 'Rôle'
    is_staff_display.admin_order_field = 'is_staff'
    
    def date_joined_display(self, obj):
        """Affiche la date d'inscription formatée"""
        if obj.date_joined:
            return obj.date_joined.strftime('%d/%m/%Y %H:%M')
        return '-'
    date_joined_display.short_description = 'Date d\'inscription'
    date_joined_display.admin_order_field = 'date_joined'
    
    # ==================== ACTIONS PERSONNALISÉES ====================
    
    def activate_users(self, request, queryset):
        """Activer les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} utilisateur(s) activé(s).')
    activate_users.short_description = "Activer les utilisateurs sélectionnés"
    
    def deactivate_users(self, request, queryset):
        """Désactiver les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} utilisateur(s) désactivé(s).')
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"
    
    def make_staff(self, request, queryset):
        """Rendre staff les utilisateurs sélectionnés"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} utilisateur(s) promu(s) staff.')
    make_staff.short_description = "Donner les droits staff"
    
    def remove_staff(self, request, queryset):
        """Retirer les droits staff"""
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'{updated} utilisateur(s) retiré(s) du staff.')
    remove_staff.short_description = "Retirer les droits staff"
    
    # ==================== PERMISSIONS ====================
    
    def has_delete_permission(self, request, obj=None):
        """Qui peut supprimer des utilisateurs"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Qui peut ajouter des utilisateurs"""
        return request.user.is_staff
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule"""
        if obj:
            return ('cin', 'date_joined', 'last_login')
        return ()


# Enregistrement
admin.site.register(TestUser, TestUserAdmin)

# Optionnel: Personnaliser le titre de l'admin
admin.site.site_header = "Administration HSE Tests"
admin.site.site_title = "HSE Tests Admin"
admin.site.index_title = "Tableau de bord"