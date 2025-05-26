from django.urls import path
from django.contrib import admin
from . import views
from django.urls import path, include
from .views import (
    delete_attendee, delete_speaker_intervention, 
    delete_session, delete_agenda_item,
    delete_attendee_type, partner_delete,
    delete_intervention_location, delete_session_organizer,
    delete_session_funding
)

urlpatterns = [
    # === PUBLIC URLS ===
    path('', views.home, name='home'),
    
    # Speakers
    path('speakers/', views.SpeakersInterventionsListView.as_view(), name='speakers'),
    path('speakers/<int:pk>/', views.SpeakersInterventionsDetailView.as_view(), name='speaker_detail'),
    
    # Sessions
    path('sessions/', views.SessionListView.as_view(), name='sessions'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    
    # Agenda
    path('agenda/', views.AgendaView.as_view(), name='agenda'),
    path('agenda/download/', views.download_agenda, name='download_agenda'),
    
    # Registration - UPDATED to use the corrected register view
    path('register/', views.register, name='register'),
    path('registration/success/', views.registration_success, name='registration_success'),
    
    # Partners
    path('partners/', views.PartnerListView.as_view(), name='partners'),
    path('partners/<int:pk>/', views.PartnerDetailView.as_view(), name='partner_detail'),
    path('partners/download/', views.download_partners_pdf, name='download_partners_pdf'),
    
    # Attendee Types - NEW public view
    path('attendee-types/', views.AttendeeTypeListView.as_view(), name='attendee_types'),
    
    # Other pages
    path('contact/', views.contact_view, name='contact'),
    path('venue/', views.venue_view, name='venue'),
    path('faq/', views.faq_view, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('policy/', views.privacy_policy, name='policy'),
    path('code_of_conduct/', views.code_of_conduct, name='code_of_conduct'),
    path('accessibility/', views.accessibility, name='accessibility'),
    path('subscribe/', views.subscribe, name='subscribe'),

    # === ADMIN/DASHBOARD URLS ===
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Speakers Management
    path('dashboard/speakers/', include([
        path('', views.SpeakersInterventionsAdminListView.as_view(), name='speaker_list'),
        path('add/', views.speaker_intervention_create, name='speaker_create'),
        path('<int:pk>/edit/', views.speaker_intervention_edit, name='speaker_edit'),
        path('<int:pk>/delete/', delete_speaker_intervention, name='delete_speaker_intervention'),
    ])),
    
    # Sessions Management
    path('dashboard/sessions/', include([
        path('', views.SessionAdminListView.as_view(), name='session_list'),
        path('add/', views.session_create, name='session_create'),
        path('<int:pk>/', views.session_detail, name='session_detail'),
        path('<int:pk>/edit/', views.session_edit, name='session_edit'),
        path('<int:pk>/delete/', delete_session, name='delete_session'),
        # Session organizers and fundings
        path('<int:session_id>/organizers/', views.manage_session_organizers, name='manage_session_organizers'),
        path('<int:session_id>/fundings/', views.manage_session_fundings, name='manage_session_fundings'),
    ])),
    
    # Agenda Management
    path('dashboard/agenda/', include([
        path('', views.AgendaAdminListView.as_view(), name='agenda_list'),
        path('add/', views.agenda_create, name='agenda_create'),
        path('<int:pk>/edit/', views.agenda_edit, name='agenda_edit'),
        path('<int:pk>/delete/', views.agenda_delete, name='agenda_delete'),
        # Alternative delete URL for compatibility
        path('delete/<int:pk>/', delete_agenda_item, name='delete_agenda_item'),
    ])),
    
    # Attendees Management - NEW CRUD operations
    path('dashboard/attendees/', include([
        path('', views.AttendeeListView.as_view(), name='attendee_list'),
        path('<int:pk>/', views.AttendeeDetailView.as_view(), name='attendee_detail'),
        path('<int:pk>/edit/', views.AttendeeUpdateView.as_view(), name='attendee_edit'),
        path('<int:pk>/delete/', delete_attendee, name='delete_attendee'),
    ])),
    
    # Attendee Types Management
    path('dashboard/attendee-types/', include([
        path('add/', views.attendee_type_create, name='attendee_type_create'),
        path('<int:pk>/edit/', views.attendee_type_edit, name='attendee_type_edit'),
        path('<int:pk>/delete/', delete_attendee_type, name='delete_attendee_type'),
    ])),
    
    # Partners Management
    path('dashboard/partners/', include([
        path('', views.PartnerAdminListView.as_view(), name='partner_admin_list'),
        path('add/', views.partner_create, name='partner_create'),
        path('<int:pk>/edit/', views.partner_edit, name='partner_edit'),
        path('<int:pk>/delete/', views.partner_delete, name='partner_delete'),
    ])),
    
    # Locations Management
    path('dashboard/locations/', include([
        path('', views.LocationAdminListView.as_view(), name='location_list'),
        path('add/', views.location_create, name='location_create'),
        path('<int:pk>/edit/', views.location_edit, name='location_edit'),
        path('<int:pk>/delete/', views.location_delete, name='location_delete'),
        # Alternative management URL
        path('manage/', views.manage_intervention_locations, name='manage_intervention_locations'),
        # Alternative delete URL for compatibility
        path('delete/<int:pk>/', delete_intervention_location, name='delete_intervention_location'),
    ])),
    
    # Session Organizers Management - NEW UPDATE operations
    path('dashboard/organizers/', include([
        path('<int:pk>/edit/', views.SessionOrganizerUpdateView.as_view(), name='organizer_edit'),
        path('<int:pk>/delete/', delete_session_organizer, name='delete_session_organizer'),
    ])),
    
    # Session Fundings Management - NEW UPDATE operations
    path('dashboard/fundings/', include([
        path('<int:pk>/edit/', views.SessionFundingUpdateView.as_view(), name='funding_edit'),
        path('<int:pk>/delete/', delete_session_funding, name='delete_session_funding'),
    ])),

    # Django Admin
    path('admin/', admin.site.urls),
]