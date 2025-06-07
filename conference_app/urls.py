from django.urls import path
from django.contrib import admin
from . import views
from django.urls import path, include
from .views import (
    delete_speaker_intervention, 
    delete_session, agenda_delete, agenda_edit,
    delete_attendee_type, partner_delete,
    delete_intervention_location,
    attendee_create, attendee_update, attendee_delete,
    organizer_list, organizer_create, organizer_edit, organizer_delete,funding_list,
    funding_delete, funding_create, funding_edit,
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
    
    # AJAX endpoint for session data
    path('api/session/<int:session_id>/data/', views.get_session_data, name='get_session_data'),
    

    # Speakers Management
    path('dashboard/speakers/', include([
        path('', views.SpeakersInterventionsAdminListView.as_view(), name='speaker_list'),
        path('<int:session_id>/', views.speaker_list, name='session_speakers'),
        path('<int:session_id>/add/', views.speaker_intervention_create, name='speaker_create'),  # Modifié : ajout de <int:session_id>
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
        # Ajout de l'URL pour les organisateurs (redirection vers organizer_list)
        path('<int:session_id>/organizers/', views.organizer_list, name='session_organizers'),
        # Ajout de l'URL pour les financements (redirection vers funding_list)
        path('<int:session_id>/fundings/', views.funding_list, name='session_fundings'),
    ])),
    
    
    # Agenda
    path('dashboard/agenda/', include([
        path('<int:session_id>/', views.agenda_list, name='agenda_list'),
        path('create/<int:session_id>/', views.agenda_create, name='agenda_create'),
        path('<int:pk>/edit/', views.agenda_edit, name='agenda_edit'),
        path('<int:pk>/delete/', views.agenda_delete, name='agenda_delete'),
    ])),

  
    
    # Attendees Management - NEW CRUD operations
    #path('dashboard/attendees/', include([
     #   path('', views.AttendeeListView.as_view(), name='attendee_list'),
      #  path('<int:pk>/', views.AttendeeDetailView.as_view(), name='attendee_detail'),
       # path('<int:pk>/edit/', views.AttendeeUpdateView.as_view(), name='attendee_edit'),
        #path('delete/<int:pk>', delete_attendee, name='delete_attendee'),
    #]#)),

    path('dashboard/attendees/', include([
        path('<int:session_id>/', views.attendee_list, name='attendee_list'),
        path('<int:session_id>/add/', views.attendee_create, name='attendee_create'),
        path('<int:pk>/edit/', views.attendee_update, name='attendee_edit'),
        path('<int:pk>/delete/<int:session_id>/', views.attendee_delete, name='attendee_delete'),
    ])),


    # Attendee Types Management
    path('dashboard/attendee-types/', include([
        path('add/', views.attendee_type_create, name='attendee_type_create'),
        path('<int:pk>/edit/', views.attendee_type_edit, name='attendee_type_edit'),
        path('<int:pk>/delete/', views.delete_attendee_type, name='delete_attendee_type'),
    ])),
    
    # Partners Management
    path('dashboard/partners/', include([
        path('', views.PartnerAdminListView.as_view(), name='partner_admin_list'),
        path('add/', views.partner_create, name='partner_create'),
        path('<int:pk>/edit/', views.partner_edit, name='partner_edit'),
        path('<int:pk>/delete/', views.partner_delete, name='partner_delete'),
        path('api/partners/<int:partner_id>/', views.get_partner_data, name='api_partner_data'),
        path('download-pdf/', views.download_partners_pdf, name='download_partners_pdf'),    
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
        path('delete/<int:pk>/', views.delete_intervention_location, name='delete_intervention_location'),
    ])),
    
    # Session Organizers Management - CLEANED UP
    path('dashboard/organizers/', include([
        path('<int:session_id>/', views.organizer_list, name='organizer_list'),
        path('<int:session_id>/add/', views.organizer_create, name='organizer_create'),
        path('<int:pk>/edit/', views.organizer_edit, name='organizer_edit'),
        path('<int:pk>/delete/', views.organizer_delete, name='organizer_delete'),
        path('<int:pk>/update/', views.SessionOrganizerUpdateView.as_view(), name='organizer_update'),
    ])),
    
    # Session Fundings Management
    path('dashboard/fundings/', include([
        path('<int:session_id>/', views.funding_list, name='funding_list'),
        path('<int:session_id>/add/', views.funding_create, name='funding_create'),
        path('<int:pk>/edit/', views.funding_edit, name='funding_edit'),
        path('<int:pk>/delete/', views.funding_delete, name='funding_delete'),  # Modifié : delete_session_funding -> funding_delete
    ])),


    # Django Admin
    path('admin/', admin.site.urls),
]