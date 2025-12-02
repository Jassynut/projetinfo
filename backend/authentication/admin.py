# authentication/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import TestUser
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms


# ==================== FORMULAIRES PERSONNALISÉS ====================

class CustomUserChangeForm(UserChangeForm):
    """Formulaire pour modifier un utilisateur dans l'admin"""
    class Meta(UserChangeForm.Meta):
        model = TestUser

class CustomUserCreationForm(UserCreationForm):
    """Formulaire pour créer un nouvel utilisateur dans l'admin"""
    class Meta(UserCreationForm.Meta):
        model = TestUser
        fields = ('cin', 'username', 'full_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False


# ==================== ADMIN PERSONNALISÉ POUR TESTUSER ====================

class TestUserAdmin(UserAdmin):
    """Interface d'administration pour TestUser"""
    
    # Formulaires
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Affichage dans la liste
    list_display = (
        'cin_display', 
        'username_display', 
        'full_name_display', 
        'email_display',
        'is_active_display', 
        'is_staff_display',
        'date_joined_display',
        'actions_buttons'
    )
    
    # Filtres
    list_filter = (
        'is_staff', 
        'is_superuser', 
        'is_active',
        'date_joined',
    )
    
    # Champs de recherche
    search_fields = (
        'cin', 
        'username', 
        'full_name', 
        'email'
    )
    
    # Organisation dans le formulaire d'édition
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('cin', 'username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('full_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
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
    
    # Configuration des colonnes dans la liste
    list_display_links = ('cin_display', 'username_display')
    list_per_page = 50
   
    def actions_buttons(self, obj):
        """Affiche des boutons d'action rapide"""
        return format_html(
            '''
            <div style="display: flex; gap: 5px;">
                <a href="{}" class="button" title="Modifier">✏️</a>
                <a href="{}" class="button" title="Supprimer">🗑️</a>
            </div>
            ''',
            f'{obj.pk}/change/',
            f'{obj.pk}/delete/'
        )
    
    # Actions personnalisées
    def activate_users(self, request, queryset):
        """Activer les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} utilisateur(s) activé(s).')
    
    def deactivate_users(self, request, queryset):
        """Désactiver les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} utilisateur(s) désactivé(s).')
    
    def make_staff(self, request, queryset):
        """Rendre staff les utilisateurs sélectionnés"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} utilisateur(s) promu(s) staff.')
    
    def remove_staff(self, request, queryset):
        """Retirer les droits staff"""
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'{updated} utilisateur(s) retiré(s) du staff.')
    
    # Configuration des permissions
    def has_delete_permission(self, request, obj=None):
        """Qui peut supprimer des utilisateurs"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Qui peut ajouter des utilisateurs"""
        return request.user.is_staff
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule"""
        if obj:
            # Pour un utilisateur existant, le CIN est en lecture seule
            return ('cin', 'date_joined', 'last_login')
        return ()
    
    # Configuration du formulaire
    def get_form(self, request, obj=None, **kwargs):
        """Personnalisation du formulaire"""
        form = super().get_form(request, obj, **kwargs)
        
        # Si on modifie un utilisateur existant, on ne peut pas changer son CIN
        if obj:
            form.base_fields['cin'].disabled = True
            form.base_fields['cin'].help_text = 'Le CIN ne peut pas être modifié'
        
        return form


# ==================== ENREGISTREMENT DES MODÈLES ====================

# Enregistrer TestUser avec l'admin personnalisé
admin.site.register(TestUser, TestUserAdmin)

# Optionnel: Personnaliser le titre de l'admin
admin.site.site_header = "Administration HSE Tests"
admin.site.site_title = "HSE Tests Admin"
admin.site.index_title = "Tableau de bord"