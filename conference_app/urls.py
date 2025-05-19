from django.urls import path
from . import views
from django.urls import path
from .views import (
    delete_attendee, delete_speaker, 
    delete_session, delete_agenda_item,
    delete_attendee_type
)


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
    
    # Admin management URLs
    path('dashboard/speaker/add/', views.speaker_create, name='speaker_create'),
    path('dashboard/speaker/<int:pk>/edit/', views.speaker_edit, name='speaker_edit'),
    path('dashboard/session/add/', views.session_create, name='session_create'),
    path('dashboard/session/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('dashboard/agenda/add/', views.agenda_create, name='agenda_create'),
    path('dashboard/agenda/<int:pk>/edit/', views.agenda_edit, name='agenda_edit'),
    path('dashboard/attendee-type/add/', views.attendee_type_create, name='attendee_type_create'),
    path('dashboard/attendee-type/<int:pk>/edit/', views.attendee_type_edit, name='attendee_type_edit'),

    path('dashboard/attendee/delete/<int:pk>/', delete_attendee, name='delete_attendee'),
    path('dashboard/speaker/delete/<int:pk>/', delete_speaker, name='delete_speaker'),
    path('dashboard/session/delete/<int:pk>/', delete_session, name='delete_session'),
    path('dashboard/agenda/delete/<int:pk>/', delete_agenda_item, name='delete_agenda_item'),
    path('dashboard/attendee-type/delete/<int:pk>/', delete_attendee_type, name='delete_attendee_type'),
]
