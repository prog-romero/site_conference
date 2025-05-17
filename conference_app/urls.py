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

    
    # Admin management URLs
    path('dashboard/speaker/add/', views.speaker_create, name='speaker_create'),
    path('dashboard/speaker/<int:pk>/edit/', views.speaker_edit, name='speaker_edit'),
    path('dashboard/session/add/', views.session_create, name='session_create'),
    path('dashboard/session/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('dashboard/agenda/add/', views.agenda_create, name='agenda_create'),
    path('dashboard/agenda/<int:pk>/edit/', views.agenda_edit, name='agenda_edit'),
    path('dashboard/attendee-type/add/', views.attendee_type_create, name='attendee_type_create'),
    path('dashboard/attendee-type/<int:pk>/edit/', views.attendee_type_edit, name='attendee_type_edit'),
]