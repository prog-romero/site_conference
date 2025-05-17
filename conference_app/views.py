from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Speaker, Session, AgendaItem, AttendeeType, Attendee
from .forms import RegistrationForm, ContactForm
from django.db.models import Q
from datetime import datetime


from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags




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

#moi
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Sauvegarde de l'inscription
            registration = form.save()
            
            # Préparation de l'email
            subject = 'Confirmation de votre inscription à Conference 2025'
            html_message = render_to_string('conference_app/email_confirmation.html', {
                'name': registration.name,
                'event_name': 'Conference 2025',
                'event_date': 'June 15-17, 2025',
                'event_location': 'Conference Center',
            })
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = registration.email
            
            # Envoi de l'email
            send_mail(
                subject,
                plain_message,
                from_email,
                [to_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return redirect('registration_success')
    else:
        form = RegistrationForm()
    
    return render(request, 'conference_app/register.html', {'form': form})

#moi
def registration_success(request):
    return render(request, 'conference_app/registration_success.html')



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

def terms(request):
    return render(request, 'conference_app/tos.html')

def privacy_policy(request):
    return render(request, 'conference_app/policy.html')

def code_of_conduct(request):
    return render(request, 'conference_app/code_of_conduct.html')

def accessibility(request):
    return render(request, 'conference_app/accessibility.html')

@login_required
def speaker_create(request):
    if request.method == 'POST':
        # Handle form submission
        speaker = Speaker.objects.create(
            name=request.POST['name'],
            title=request.POST['title'],
            organization=request.POST['organization'],
            bio=request.POST['bio']
        )
        if 'photo' in request.FILES:
            speaker.photo = request.FILES['photo']
            speaker.save()
        messages.success(request, 'Speaker added successfully.')
        return redirect('dashboard')
    return render(request, 'admin/speaker_form.html')

@login_required
def speaker_edit(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        speaker.name = request.POST['name']
        speaker.title = request.POST['title']
        speaker.organization = request.POST['organization']
        speaker.bio = request.POST['bio']
        if 'photo' in request.FILES:
            speaker.photo = request.FILES['photo']
        speaker.save()
        messages.success(request, 'Speaker updated successfully.')
        return redirect('dashboard')
    return render(request, 'admin/speaker_form.html', {'speaker': speaker})

@login_required
def session_create(request):
    if request.method == 'POST':
        # Handle form submission
        session = Session.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            date=request.POST['date'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            track=request.POST['track'],
            location=request.POST['location']
        )
        session.speakers.set(request.POST.getlist('speakers'))
        messages.success(request, 'Session added successfully.')
        return redirect('dashboard')
    context = {
        'track_choices': Session.TRACK_CHOICES,
        'speakers': Speaker.objects.all()
    }
    return render(request, 'admin/session_form.html', context)

@login_required
def session_edit(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        session.title = request.POST['title']
        session.description = request.POST['description']
        session.date = request.POST['date']
        session.start_time = request.POST['start_time']
        session.end_time = request.POST['end_time']
        session.track = request.POST['track']
        session.location = request.POST['location']
        session.speakers.set(request.POST.getlist('speakers'))
        session.save()
        messages.success(request, 'Session updated successfully.')
        return redirect('dashboard')
    context = {
        'session': session,
        'track_choices': Session.TRACK_CHOICES,
        'speakers': Speaker.objects.all()
    }
    return render(request, 'admin/session_form.html', context)

@login_required
def agenda_create(request):
    if request.method == 'POST':
        # Handle form submission
        agenda_item = AgendaItem.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            date=request.POST['date'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            item_type=request.POST['item_type'],
            location=request.POST['location'],
            session_id=request.POST['session'] or None
        )
        messages.success(request, 'Agenda item added successfully.')
        return redirect('dashboard')
    context = {
        'item_type_choices': AgendaItem.ITEM_TYPE_CHOICES,
        'sessions': Session.objects.all()
    }
    return render(request, 'admin/agenda_form.html', context)

@login_required
def agenda_edit(request, pk):
    agenda_item = get_object_or_404(AgendaItem, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        agenda_item.title = request.POST['title']
        agenda_item.description = request.POST['description']
        agenda_item.date = request.POST['date']
        agenda_item.start_time = request.POST['start_time']
        agenda_item.end_time = request.POST['end_time']
        agenda_item.item_type = request.POST['item_type']
        agenda_item.location = request.POST['location']
        agenda_item.session_id = request.POST['session'] or None
        agenda_item.save()
        messages.success(request, 'Agenda item updated successfully.')
        return redirect('dashboard')
    context = {
        'agenda_item': agenda_item,
        'item_type_choices': AgendaItem.ITEM_TYPE_CHOICES,
        'sessions': Session.objects.all()
    }
    return render(request, 'admin/agenda_form.html', context)

@login_required
def attendee_type_create(request):
    if request.method == 'POST':
        # Handle form submission
        AttendeeType.objects.create(
            name=request.POST['name'],
            description=request.POST['description']
        )
        messages.success(request, 'Attendee type added successfully.')
        return redirect('dashboard')
    return render(request, 'admin/attendee_type_form.html')

@login_required
def attendee_type_edit(request, pk):
    attendee_type = get_object_or_404(AttendeeType, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        attendee_type.name = request.POST['name']
        attendee_type.description = request.POST['description']
        attendee_type.save()
        messages.success(request, 'Attendee type updated successfully.')
        return redirect('dashboard')
    return render(request, 'admin/attendee_type_form.html', {'attendee_type': attendee_type})
