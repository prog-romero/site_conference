from django.urls import path, include
from django.contrib import admin
from . import views
from .views import (
    # Vues existantes
    accessibility, code_of_conduct, contact_view, faq_view, home, privacy_policy, register, registration_success, subscribe, terms, venue_view,
    AgendaView, agenda_download,
    PartnerListView, PartnerDetailView, partners_download_pdf,
    SessionListView, SessionDetailView,
    SpeakersInterventionsListView, SpeakersInterventionsDetailView,
    AttendeeTypeListView,
    
    # Vues du Dashboard
    dashboard_view,
    
    # Agenda views
    agenda_create, agenda_delete, agenda_edit, agenda_list,
    # Attendee views
    attendee_create, attendee_delete, attendee_update, attendee_list, AttendeeDetailView, AttendeeListView, AttendeeUpdateView,
    # Attendee type views
    attendee_type_create, attendee_type_edit, attendee_type_delete,
    # Funding views
    funding_create, funding_delete, funding_edit, funding_list, SessionFundingUpdateView,
    # Location views
    location_create, location_delete, location_edit, location_manage, location_delete_intervention, LocationAdminListView,
    # Organizer views
    organizer_create, organizer_delete, organizer_edit, organizer_list, organizer_list_public, SessionOrganizerUpdateView,
    # Partner views
    partner_create, partner_delete, partner_edit, partner_get_data, PartnerAdminListView,
    # Session views
    session_create, session_delete, session_edit, session_get_data, SessionAdminListView,
    # Speaker views
    speaker_create, speaker_delete, speaker_edit, speaker_list, SpeakersInterventionsAdminListView,

    # ▼▼▼▼ VUES POUR LES NOUVELLES CLASSES IMPORTÉES ▼▼▼▼
    gallery_list, gallery_photo_edit, gallery_photo_delete,
    volunteer_list, volunteer_create, volunteer_edit, volunteer_delete,
)

urlpatterns = [
    # ========================================================================
    # PUBLIC URLS - URLs accessibles au public
    # ========================================================================
    
    # --- Accueil ---
    path('', views.home, name='home'),
    
    # --- Organisateurs (liste publique) ---
    path('organizers/session/<int:session_id>/', views.organizer_list_public, name='organizer_list_public'),

    # --- Accessibilité ---
    path('accessibility/', views.accessibility, name='accessibility'),
    
    # --- Agenda ---
    path('agenda/', views.AgendaView.as_view(), name='agenda'),
    path('agenda/download/', views.agenda_download, name='agenda_download'),
    
    # --- Code de conduite ---
    path('code_of_conduct/', views.code_of_conduct, name='code_of_conduct'),
    
    # --- Contact ---
    path('contact/', views.contact_view, name='contact'),
    
    # --- FAQ ---
    path('faq/', views.faq_view, name='faq'),
    
    # --- Inscription ---
    path('register/', views.register, name='register'),
    path('registration/success/', views.registration_success, name='registration_success'),
    
    # --- Partenaires ---
    path('partners/', views.PartnerListView.as_view(), name='partners'),
    path('partners/<int:pk>/', views.PartnerDetailView.as_view(), name='partner_detail'),
    path('partners/download/', views.partners_download_pdf, name='partners_download_pdf'),
    
    # --- Politique de confidentialité ---
    path('policy/', views.privacy_policy, name='policy'),
    
    # --- Sessions ---
    path('sessions/', views.SessionListView.as_view(), name='sessions'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    
    # --- Intervenants ---
    path('speakers/', views.SpeakersInterventionsListView.as_view(), name='speakers'),
    path('speakers/<int:pk>/', views.SpeakersInterventionsDetailView.as_view(), name='speaker_detail'),
    
    # --- Abonnement ---
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # --- Conditions d'utilisation ---
    path('terms/', views.terms, name='terms'),
    
    # --- Types de participants ---
    path('attendee-types/', views.AttendeeTypeListView.as_view(), name='attendee_types'),
    
    # --- Lieu ---
    path('venue/', views.venue_view, name='venue'),

    # ========================================================================
    # ADMIN/DASHBOARD URLS - URLs d'administration
    # ========================================================================
    
    # --- Tableau de bord ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # --- API AJAX ---
    path('api/session/<int:session_id>/data/', views.session_get_data, name='session_get_data'),

    # --- Gestion de l'agenda ---
    path('dashboard/agenda/', include([
        path('<int:session_id>/', views.agenda_list, name='agenda_list'),
        path('create/<int:session_id>/', views.agenda_create, name='agenda_create'),
        path('<int:pk>/edit/', views.agenda_edit, name='agenda_edit'),
        path('<int:pk>/delete/', views.agenda_delete, name='agenda_delete'),
    ])),

    # --- Gestion des participants ---
    path('dashboard/attendees/', include([
        path('', views.AttendeeListView.as_view(), name='attendee_list_all'), # Ajout d'une route pour voir tous les participants
        path('<int:session_id>/', views.attendee_list, name='attendee_list'),
        path('<int:session_id>/add/', views.attendee_create, name='attendee_create'),
        path('<int:pk>/edit/', views.attendee_update, name='attendee_edit'),
        path('<int:pk>/delete/', views.attendee_delete, name='attendee_delete'),
    ])),

    # ▼▼▼▼ NOUVELLE URL POUR LA PAGE GALERIE PUBLIQUE ▼▼▼▼
    path('gallery/', views.gallery_page, name='gallery_page_public'),

    # --- Gestion des types de participants ---
    path('dashboard/attendee-types/', include([
        path('', views.AttendeeTypeListView.as_view(), name='attendee_type_list'),
        path('add/', views.attendee_type_create, name='attendee_type_create'),
        path('<int:pk>/edit/', views.attendee_type_edit, name='attendee_type_edit'),
        path('<int:pk>/delete/', views.attendee_type_delete, name='attendee_type_delete'),
    ])),
    
    # --- Gestion des financements ---
    path('dashboard/fundings/', include([
        path('<int:session_id>/', views.funding_list, name='funding_list'),
        path('<int:session_id>/add/', views.funding_create, name='funding_create'),
        path('<int:pk>/edit/', views.funding_edit, name='funding_edit'),
        path('<int:pk>/delete/', views.funding_delete, name='funding_delete'),
    ])),

    # --- Gestion des lieux ---
    path('dashboard/locations/', include([
        path('', views.LocationAdminListView.as_view(), name='location_list'),
        path('add/', views.location_create, name='location_create'),
        path('<int:pk>/edit/', views.location_edit, name='location_edit'),
        path('<int:pk>/delete/', views.location_delete, name='location_delete'),
        path('manage/', views.location_manage, name='location_manage'),
        path('delete/<int:pk>/', views.location_delete_intervention, name='location_delete_intervention'),
    ])),

    # --- Gestion des organisateurs ---
    path('dashboard/organizers/', include([
        path('<int:session_id>/', views.organizer_list, name='organizer_list'),
        path('<int:session_id>/add/', views.organizer_create, name='organizer_create'),
        path('<int:pk>/edit/', views.organizer_edit, name='organizer_edit'),
        path('<int:pk>/delete/', views.organizer_delete, name='organizer_delete'),
        path('<int:pk>/update/', views.SessionOrganizerUpdateView.as_view(), name='organizer_update'),
    ])),
    
    # --- Gestion des partenaires ---
    path('dashboard/partners/', include([
        path('', views.PartnerAdminListView.as_view(), name='partner_admin_list'),
        path('add/', views.partner_create, name='partner_create'),
        path('<int:pk>/edit/', views.partner_edit, name='partner_edit'),
        path('<int:pk>/delete/', views.partner_delete, name='partner_delete'),
        path('api/partners/<int:partner_id>/', views.partner_get_data, name='partner_get_data'),
        path('download-pdf/', views.partners_download_pdf, name='partners_download_pdf'),    
    ])),
    
    # --- Gestion des sessions ---
    path('dashboard/sessions/', include([
        path('', views.SessionAdminListView.as_view(), name='session_list'),
        path('add/', views.session_create, name='session_create'),
        path('<int:pk>/', views.session_detail, name='session_detail'),
        path('<int:pk>/edit/', views.session_edit, name='session_edit'),
        path('<int:pk>/delete/', views.session_delete, name='session_delete'),
        path('<int:session_id>/organizers/', views.organizer_list, name='session_organizers'),
        path('<int:session_id>/fundings/', views.funding_list, name='session_fundings'),
    ])),
    
    # --- Gestion des intervenants ---
    path('dashboard/speakers/', include([
        path('', views.SpeakersInterventionsAdminListView.as_view(), name='speaker_list'),
        path('<int:session_id>/', views.speaker_list, name='session_speakers'),
        path('<int:session_id>/add/', views.speaker_create, name='speaker_create'),
        path('<int:pk>/edit/', views.speaker_edit, name='speaker_edit'),
        path('<int:pk>/delete/', views.speaker_delete, name='speaker_delete'),
    ])),
    
    # ▼▼▼▼ NOUVELLES URLS POUR LA GALERIE ET LES VOLONTAIRES ▼▼▼▼

    # --- Gestion de la Galerie (Photos) ---
    path('dashboard/gallery/', include([
        path('<int:session_id>/', views.gallery_list, name='gallery_list'),
        # La création se fait depuis la page de liste, pas besoin d'une URL séparée
        path('photo/<int:pk>/edit/', views.gallery_photo_edit, name='gallery_photo_edit'),
        path('photo/<int:pk>/delete/', views.gallery_photo_delete, name='gallery_photo_delete'),
    ])),
    
    # --- Gestion des Volontaires ---
    path('dashboard/volunteers/', include([
        path('<int:session_id>/', views.volunteer_list, name='volunteer_list'),
        path('<int:session_id>/add/', views.volunteer_create, name='volunteer_create'),
        path('<int:pk>/edit/', views.volunteer_edit, name='volunteer_edit'),
        path('<int:pk>/delete/', views.volunteer_delete, name='volunteer_delete'),
    ])),

    # ▲▲▲▲ FIN DES NOUVELLES URLS ▲▲▲▲

    # --- Django Admin ---
    path('admin/', admin.site.urls),
]