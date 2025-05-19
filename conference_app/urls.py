from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('speakers/', views.SpeakerListView.as_view(), name='speakers'),
    path('speakers/<int:pk>/', views.SpeakerDetailView.as_view(), name='speaker_detail'),
    path('sessions/', views.SessionListView.as_view(), name='sessions'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('agenda/', views.AgendaView.as_view(), name='agenda'),
    path('register/', views.register_view, name='register'),
    path('contact/', views.contact_view, name='contact'),
    path('venue/', views.venue_view, name='venue'),
    path('faq/', views.faq_view, name='faq'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

#me
    path('terms/', views.terms, name='terms'),
    path('policy/', views.privacy_policy, name='policy'),
    path('code_of_conduct/', views.code_of_conduct, name='code_of_conduct'),
    path('accessibility/', views.accessibility, name='accessibility'),

    path('admin/', admin.site.urls),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('agenda/download/', views.download_agenda, name='download_agenda'),
    path('partners/', views.PartnerListView.as_view(), name='partners'),  # Nouvelle URL
    path('partners/<int:pk>/', views.PartnerDetailView.as_view(), name='partner_detail'),  # Nouvelle URL
    path('partners/download/', views.download_partners_pdf, name='download_partners_pdf'),  # Nouvelle URL
    
    

    # Admin management URLs
    path('dashboard/speaker/add/', views.speaker_create, name='speaker_create'),
    path('dashboard/speaker/<int:pk>/edit/', views.speaker_edit, name='speaker_edit'),
    path('dashboard/session/add/', views.session_create, name='session_create'),
    path('dashboard/session/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('dashboard/agenda/add/', views.agenda_create, name='agenda_create'),
    path('dashboard/agenda/<int:pk>/edit/', views.agenda_edit, name='agenda_edit'),
    path('dashboard/attendee-type/add/', views.attendee_type_create, name='attendee_type_create'),
    path('dashboard/attendee-type/<int:pk>/edit/', views.attendee_type_edit, name='attendee_type_edit'),



    # Dans urlpatterns, ajoute ces paths pour la gestion des partenaires dans le dashboard
    path('dashboard/partners/', views.PartnerAdminListView.as_view(), name='partner_list'),
    path('dashboard/partner/add/', views.partner_create, name='partner_create'),
    path('dashboard/partner/<int:pk>/edit/', views.partner_edit, name='partner_edit'),
    path('dashboard/partner/<int:pk>/delete/', views.partner_delete, name='partner_delete'),
]