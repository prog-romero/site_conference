from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Speaker, Session, AgendaItem, AttendeeType, Attendee
from .forms import RegistrationForm, ContactForm
from django.db.models import Q
from datetime import datetime

def home(request):
    featured_speakers = Speaker.objects.all()[:4]
    upcoming_sessions = Session.objects.filter(date__gte=datetime.now().date()).order_by('date', 'start_time')[:5]
    attendee_types = AttendeeType.objects.all()
    
    context = {
        'featured_speakers': featured_speakers,
        'upcoming_sessions': upcoming_sessions,
        'attendee_types': attendee_types,
    }
    return render(request, 'conference_app/home.html', context)

class SpeakerListView(ListView):
    model = Speaker
    template_name = 'conference_app/speakers.html'
    context_object_name = 'speakers'

class SpeakerDetailView(DetailView):
    model = Speaker
    template_name = 'conference_app/speaker_detail.html'
    context_object_name = 'speaker'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.object.sessions.all()
        return context

class SessionListView(ListView):
    model = Session
    template_name = 'conference_app/sessions.html'
    context_object_name = 'sessions'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        track = self.request.GET.get('track')
        search = self.request.GET.get('search')
        
        if track:
            queryset = queryset.filter(track=track)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(speakers__name__icontains=search)
            ).distinct()
            
        return queryset.order_by('date', 'start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = dict(Session.TRACK_CHOICES)
        return context

class SessionDetailView(DetailView):
    model = Session
    template_name = 'conference_app/session_detail.html'
    context_object_name = 'session'

class AgendaView(TemplateView):
    template_name = 'conference_app/agenda.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group agenda items by date
        agenda_by_date = {}
        agenda_items = AgendaItem.objects.all().order_by('date', 'start_time')
        
        for item in agenda_items:
            date_str = item.date.strftime('%Y-%m-%d')
            if date_str not in agenda_by_date:
                agenda_by_date[date_str] = {
                    'date': item.date,
                    'date_formatted': item.date.strftime('%A, %B %d, %Y'),
                    'items': []
                }
            agenda_by_date[date_str]['items'].append(item)
        
        context['agenda_days'] = agenda_by_date.values()
        return context

@login_required
def dashboard_view(request):
    context = {
        'total_registrations': Attendee.objects.count(),
        'total_sessions': Session.objects.count(),
        'total_speakers': Speaker.objects.count(),
        'recent_registrations': Attendee.objects.all().order_by('-registration_date')[:10],
        'speakers': Speaker.objects.all(),
        'sessions': Session.objects.all().order_by('date', 'start_time'),
        'agenda_items': AgendaItem.objects.all().order_by('date', 'start_time'),
        'attendee_types': AttendeeType.objects.all(),
    }
    return render(request, 'conference_app/dashboard.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! We look forward to seeing you at the conference.')
            return redirect('home')
    else:
        form = RegistrationForm()
    
    return render(request, 'conference_app/register.html', {'form': form})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process form data (in a real app, send email)
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'conference_app/contact.html', {'form': form})

def venue_view(request):
    return render(request, 'conference_app/venue.html')

def faq_view(request):
    return render(request, 'conference_app/faq.html')