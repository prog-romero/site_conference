
# conference_app/admin.py

from django.contrib import admin
from .models import (
    SpeakersInterventions, Session, AgendaItem, Attendee, AttendeeType, 
    Partner, InterventionLocation, SessionOrganizer, SessionFunding, Subscriber,
    MenuPhoto, StudentVolunteer
)
from django.utils.html import format_html

# --- CONFIGURATIONS POUR LES FORMULAIRES INLINE ---
class SessionOrganizerInline(admin.TabularInline):
    model = SessionOrganizer
    extra = 1
    fields = ('name', 'organization', 'photo', 'order', 'is_primary')
    ordering = ('order',)

class MenuPhotoInline(admin.TabularInline):
    """Permet de gérer la galerie photo directement depuis la page d'une session."""
    model = MenuPhoto
    extra = 1
    # ▼▼▼▼ 'date' AJOUTÉ AUX CHAMPS DE L'INLINE ▼▼▼▼
    fields = ('photo', 'date', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ('order',)
    
    def image_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" />', obj.photo.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu'


class StudentVolunteerInline(admin.TabularInline):
    model = StudentVolunteer
    extra = 1
    fields = ('full_name', 'institute', 'role', 'photo', 'order')
    ordering = ('order',)

# --------------------------------------------------------------------------

@admin.register(SpeakersInterventions)
class SpeakersInterventionsAdmin(admin.ModelAdmin):
    # ▼▼▼▼ 'slides_status' AJOUTÉ À list_display ▼▼▼▼
    list_display = ('name', 'title', 'organization', 'session', 'intervention_type', 'is_remote', 'slides_status')
    list_filter = ('intervention_type', 'is_remote', 'session', 'gender', 'slides_status')
    search_fields = ('name', 'organization', 'bio', 'title')
    filter_horizontal = ('countries',)
    autocomplete_fields = ['session', 'location']
    list_per_page = 20
    
    # ▼▼▼▼ NOUVEAUX CHAMPS AJOUTÉS AUX fieldsets ▼▼▼▼
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'title', 'organization', 'bio', 'photo', 'gender')
        }),
        ('Intervention Details', {
            'fields': ('session', 'intervention_type', 'location', 'is_remote')
        }),
        ('Presentation Slides', {
            'fields': ('slides_status', 'slides_file'),
            'description': "Set status to 'Available' to enable the download link."
        }),
        ('Intervention Countries', {
            'fields': ('countries',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'location')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'track', 'duration_days', 'is_hybrid', 'speakers_count', 'attendees_count')
    list_filter = ('start_date', 'track', 'is_hybrid', 'locations')
    search_fields = ('title', 'description')
    filter_horizontal = ('locations',)
    readonly_fields = ('duration_days',)
    date_hierarchy = 'start_date'
    list_per_page = 20
    
    fieldsets = (
        ('General Information', {
            'fields': ('title', 'description', 'logo', 'track', 'is_hybrid')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'duration_days')
        }),
        ('Locations', {
            'fields': ('location', 'locations'),
        }),
    )
    
    inlines = [
        SessionOrganizerInline,
        MenuPhotoInline,
        StudentVolunteerInline,
    ]
    
    def speakers_count(self, obj):
        return obj.speakers.count()
    speakers_count.short_description = 'Speakers'
    
    def attendees_count(self, obj):
        return obj.attendees.count()
    attendees_count.short_description = 'Attendees'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('speakers', 'attendees')

@admin.register(AgendaItem)
class AgendaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'end_time', 'item_type', 'location', 'session')
    list_filter = ('date', 'item_type', 'location', 'session')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'
    autocomplete_fields = ['session', 'location', 'speaker_intervention']
    list_per_page = 25
    
    # ▼▼▼▼ 'speaker_intervention' AJOUTÉ AU fieldset ▼▼▼▼
    fieldsets = (
        ('General Information', {
            'fields': ('title', 'description', 'item_type')
        }),
        ('Scheduling', {
            'fields': ('date', 'start_time', 'end_time')
        }),
        ('Associations', {
            'fields': ('session', 'location', 'speaker_intervention')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'location', 'speaker_intervention')


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'job_title', 'session', 'registration_date')
    list_filter = ('attendee_type', 'registration_date', 'session')
    search_fields = ('name', 'email', 'company', 'job_title')
    date_hierarchy = 'registration_date'
    autocomplete_fields = ['session']
    list_per_page = 25
    readonly_fields = ('registration_date',)
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('name', 'email', 'company', 'job_title')
        }),
        ('Inscription', {
            'fields': ('session', 'attendee_type', 'registration_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'attendee_type')

@admin.register(AttendeeType)
class AttendeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'attendees_count')
    search_fields = ('name', 'description')
    
    def attendees_count(self, obj):
        return obj.attendee_set.count()
    attendees_count.short_description = 'Nombre d\'inscrits'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attendee_set')

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner_type', 'website', 'country', 'is_active', 'created_at', 'fundings_count')
    search_fields = ('name', 'description', 'country')
    list_filter = ('is_active', 'partner_type', 'created_at', 'country')
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'logo')
        }),
        ('Contact', {
            'fields': ('website', 'country')
        }),
        ('Classification', {
            'fields': ('partner_type', 'is_active')
        }),
    )
    
    def fundings_count(self, obj):
        return obj.fundings.count()
    fundings_count.short_description = 'Financements'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('fundings')

@admin.register(InterventionLocation)
class InterventionLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_primary', 'sessions_count', 'speakers_count')
    list_filter = ('is_primary', 'country')
    search_fields = ('name', 'country')
    
    def sessions_count(self, obj):
        return obj.sessions.count()
    sessions_count.short_description = 'Sessions'
    
    def speakers_count(self, obj):
        return obj.speakers.count()
    speakers_count.short_description = 'Speakers'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('sessions', 'speakers')

@admin.register(SessionOrganizer)
class SessionOrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'session', 'order', 'is_primary')
    list_filter = ('is_primary', 'session')
    search_fields = ('name', 'organization')
    ordering = ('session', 'order')
    autocomplete_fields = ['session']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('name', 'organization', 'photo')
        }),
        ('Organisation', {
            'fields': ('session', 'order', 'is_primary')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')

@admin.register(SessionFunding)
class SessionFundingAdmin(admin.ModelAdmin):
    list_display = ('partner', 'session', 'funding_type', 'amount', 'country', 'covers_participants', 'created_at')
    list_filter = ('funding_type', 'session', 'partner', 'country', 'created_at')
    search_fields = ('description', 'country', 'partner__name', 'session__title')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['partner', 'session']
    list_per_page = 20
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('session', 'partner', 'funding_type')
        }),
        ('Détails du financement', {
            'fields': ('description', 'amount', 'covers_participants')
        }),
        ('Localisation', {
            'fields': ('country',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('partner', 'session')

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')
    search_fields = ('email',)
    date_hierarchy = 'date_subscribed'
    readonly_fields = ('date_subscribed',)
    list_per_page = 50

# --- GESTION DES NOUVEAUX MODÈLES ---
@admin.register(MenuPhoto)
class MenuPhotoAdmin(admin.ModelAdmin):
    # ▼▼▼▼ 'date' AJOUTÉ À list_display ET list_filter ▼▼▼▼
    list_display = ('caption', 'session', 'date', 'order', 'image_preview')
    list_filter = ('session', 'date')
    search_fields = ('caption', 'description')
    list_editable = ('order',)
    autocomplete_fields = ['session']
    readonly_fields = ('image_preview',)
    
    # ▼▼▼▼ 'date' AJOUTÉ AU fieldset POUR LE FORMULAIRE DE DÉTAIL ▼▼▼▼
    fieldsets = (
        (None, {
            'fields': ('session', ('photo', 'image_preview'))
        }),
        ('Details', {
            'fields': ('caption', 'description', 'date', 'order')
        }),
    )
    
    def image_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="150" />', obj.photo.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu'
    

@admin.register(StudentVolunteer)
class StudentVolunteerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'institute', 'session', 'role', 'order')
    list_filter = ('session', 'institute')
    search_fields = ('full_name', 'institute', 'role')
    list_editable = ('order',)
    autocomplete_fields = ['session']


# --- CONFIGURATION GLOBALE DU SITE ADMIN ---

admin.site.site_header = "Conference 2025 Administration"
admin.site.site_title = "Conference 2025 Admin"
admin.site.index_title = "Bienvenue dans l'administration de Conference 2025"