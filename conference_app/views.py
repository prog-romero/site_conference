from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SpeakersInterventions, Session, AgendaItem, AttendeeType, Attendee, Partner, InterventionLocation, SessionFunding, SessionOrganizer
from .forms import RegistrationForm, ContactForm, SpeakersInterventionsForm
from django.db.models import Q
from datetime import datetime
from .forms import SubscribeForm, PartnerForm, SessionForm, SessionOrganizerForm, SessionFundingForm, InterventionLocationForm, AgendaItemForm

from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from io import StringIO
from django.utils.timezone import localtime
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def home(request):
    # Récupérer les intervenants mis en avant
    featured_speakers = SpeakersInterventions.objects.all()[:4]
    
    # Récupérer les sessions à venir
    today = timezone.now().date()
    upcoming_sessions = Session.objects.filter(start_date__gte=today).order_by('start_date')[:5]
    latest_session = Session.get_current_session()
    
    attendee_types = AttendeeType.objects.all()
    partners = Partner.objects.filter(is_active=True).order_by('name')
    
    context = {
        'featured_speakers': featured_speakers,
        'upcoming_sessions': upcoming_sessions,
        'attendee_types': attendee_types,
        'partners': partners,
        'latest_session': latest_session,
    }
    return render(request, 'conference_app/home.html', context)

# === SPEAKERS VIEWS ===
class SpeakersInterventionsListView(ListView):
    model = SpeakersInterventions
    template_name = 'conference_app/speakers.html'
    context_object_name = 'speakers'

class SpeakersInterventionsDetailView(DetailView):
    model = SpeakersInterventions
    template_name = 'conference_app/speaker_detail.html'
    context_object_name = 'speaker'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = self.object.session
        return context

class SpeakersInterventionsAdminListView(LoginRequiredMixin, ListView):
    model = SpeakersInterventions
    template_name = 'conference_app/admin/speaker_list.html'
    context_object_name = 'speakers'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Gestion des intervenants"
        return context

@login_required
def speaker_intervention_create(request):
    if request.method == 'POST':
        form = SpeakersInterventionsForm(request.POST, request.FILES)
        if form.is_valid():
            speaker = form.save()
            messages.success(request, 'Intervenant ajouté avec succès.')
            return redirect('dashboard')
    else:
        form = SpeakersInterventionsForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un intervenant',
    }
    return render(request, 'admin/speaker_form.html', context)

@login_required
def speaker_intervention_edit(request, pk):
    speaker = get_object_or_404(SpeakersInterventions, pk=pk)
    if request.method == 'POST':
        form = SpeakersInterventionsForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            speaker = form.save()
            messages.success(request, 'Intervenant mis à jour avec succès.')
            return redirect('dashboard')
    else:
        form = SpeakersInterventionsForm(instance=speaker)
    
    context = {
        'form': form,
        'speaker': speaker,
        'title': f'Modifier l\'intervenant: {speaker.name}',
    }
    return render(request, 'admin/speaker_form.html', context)

@login_required
def delete_speaker_intervention(request, pk):
    speaker = get_object_or_404(SpeakersInterventions, pk=pk)
    if request.method == 'POST':
        speaker_name = speaker.name
        speaker.delete()
        messages.success(request, f"Intervenant {speaker_name} supprimé avec succès.")
        return redirect('dashboard')
    return redirect('dashboard')

# === SESSIONS VIEWS ===
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
            
        return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = dict(Session.TRACK_CHOICES)
        return context

class SessionDetailView(DetailView):
    model = Session
    template_name = 'conference_app/session_detail.html'
    context_object_name = 'session'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['speakers'] = self.object.speakers.all()
        return context

class SessionAdminListView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'conference_app/admin/session_list.html'
    context_object_name = 'sessions'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Gestion des sessions"
        return context

@login_required
def session_create(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save()
            messages.success(request, 'Session ajoutée avec succès.')
            return redirect('dashboard')
    else:
        form = SessionForm()
    
    context = {
        'form': form,
        'title': 'Ajouter une session',
    }
    return render(request, 'admin/session_form.html', context)

@login_required
def session_edit(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            session = form.save()
            messages.success(request, 'Session mise à jour avec succès.')
            return redirect('dashboard')
    else:
        form = SessionForm(instance=session)
    
    context = {
        'form': form,
        'session': session,
        'title': 'Modifier la session',
    }
    return render(request, 'admin/session_form.html', context)

@login_required
def delete_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        session_title = session.title
        session.delete()
        messages.success(request, f"Session '{session_title}' has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def session_detail(request, pk):
    session = get_object_or_404(Session, pk=pk)
    organizers = session.organizers.all().order_by('order')
    fundings = session.fundings.all()
    agenda_items = session.agenda_items.all().order_by('date', 'start_time')
    speakers = session.speakers.all()
    
    # Formulaires pour ajouter des organisateurs et financements
    organizer_form = SessionOrganizerForm()
    funding_form = SessionFundingForm()
    speaker_form = SpeakersInterventionsForm(initial={'session': session})
    
    if request.method == 'POST':
        if 'add_organizer' in request.POST:
            organizer_form = SessionOrganizerForm(request.POST)
            if organizer_form.is_valid():
                organizer = organizer_form.save(commit=False)
                organizer.session = session
                organizer.save()
                messages.success(request, 'Organisateur ajouté avec succès.')
                return redirect('session_detail', pk=session.id)
        
        elif 'add_funding' in request.POST:
            funding_form = SessionFundingForm(request.POST)
            if funding_form.is_valid():
                funding = funding_form.save(commit=False)
                funding.session = session
                funding.save()
                messages.success(request, 'Financement ajouté avec succès.')
                return redirect('session_detail', pk=session.id)
                
        elif 'add_speaker' in request.POST:
            speaker_form = SpeakersInterventionsForm(request.POST, request.FILES)
            if speaker_form.is_valid():
                speaker = speaker_form.save(commit=False)
                speaker.session = session
                speaker.save()
                messages.success(request, 'Intervenant ajouté avec succès.')
                return redirect('session_detail', pk=session.id)
    
    context = {
        'session': session,
        'organizers': organizers,
        'fundings': fundings,
        'agenda_items': agenda_items,
        'speakers': speakers,
        'organizer_form': organizer_form,
        'funding_form': funding_form,
        'speaker_form': speaker_form,
        'partners': Partner.objects.filter(is_active=True),
        'title': f'Détails de la session: {session.title}',
    }
    return render(request, 'conference_app/session_detail.html', context)

# === AGENDA VIEWS ===
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

class AgendaAdminListView(LoginRequiredMixin, ListView):
    model = AgendaItem
    template_name = 'conference_app/admin/agenda_list.html'
    context_object_name = 'agenda_items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Gestion des éléments d'agenda"
        return context

@login_required
def agenda_create(request):
    if request.method == 'POST':
        form = AgendaItemForm(request.POST)
        if form.is_valid():
            agenda_item = form.save()
            messages.success(request, 'Élément d\'agenda ajouté avec succès.')
            return redirect('dashboard')
    else:
        # Pré-remplir avec la session si fournie dans l'URL
        session_id = request.GET.get('session')
        initial = {}
        if session_id:
            try:
                session = Session.objects.get(pk=session_id)
                initial['session'] = session
            except Session.DoesNotExist:
                pass
        form = AgendaItemForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Ajouter un élément d\'agenda',
    }
    return render(request, 'admin/agenda_form.html', context)

@login_required
def agenda_edit(request, pk):
    agenda_item = get_object_or_404(AgendaItem, pk=pk)
    if request.method == 'POST':
        form = AgendaItemForm(request.POST, instance=agenda_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Élément d\'agenda mis à jour avec succès.')
            return redirect('dashboard')
    else:
        form = AgendaItemForm(instance=agenda_item)
    
    context = {
        'form': form,
        'agenda_item': agenda_item,
        'title': f'Modifier l\'élément d\'agenda: {agenda_item.title}',
    }
    return render(request, 'admin/agenda_form.html', context)

@login_required
def agenda_delete(request, pk):
    agenda_item = get_object_or_404(AgendaItem, pk=pk)
    if request.method == 'POST':
        agenda_item.delete()
        messages.success(request, 'Élément d\'agenda supprimé avec succès.')
        return redirect('agenda_list')
    
    context = {
        'agenda_item': agenda_item,
        'title': f'Supprimer l\'élément d\'agenda: {agenda_item.title}',
    }
    return render(request, 'conference_app/admin/agenda_confirm_delete.html', context)

@login_required
def delete_agenda_item(request, pk):
    agenda_item = get_object_or_404(AgendaItem, pk=pk)
    if request.method == 'POST':
        item_title = agenda_item.title
        agenda_item.delete()
        messages.success(request, f"Agenda item '{item_title}' has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

def download_agenda(request):
    # Récupérer les éléments de l'agenda
    agenda_items = AgendaItem.objects.all().order_by('date', 'start_time')
    
    # Regrouper les éléments par date
    dates = agenda_items.values_list('date', flat=True).distinct()
    
    agenda_days = []
    for date in dates:
        items = agenda_items.filter(date=date)
        agenda_days.append({
            'date': date,
            'date_formatted': date.strftime("%A, %B %d, %Y"),
            'items': items
        })
    
    # Créer un buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le canvas PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Titre du document
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(300, 750, "Conference Agenda")
    p.setFont("Helvetica", 12)
    
    y_position = 700  # Position verticale initiale
    
    for day in agenda_days:
        # Titre du jour
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, day['date_formatted'])
        y_position -= 20
        
        # Préparer les données du tableau
        data = [["Time", "Session", "Type", "Location"]]
        
        for item in day['items']:
            time_str = f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}"
            location_name = item.location.name if item.location else ""
            
            data.append([
                time_str,
                item.title,
                item.get_item_type_display(),
                location_name
            ])
        
        # Créer le tableau
        table = Table(data, colWidths=[100, 200, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        # Dessiner le tableau
        table_height = len(data) * 20
        
        # Vérifier s'il y a assez d'espace sur la page actuelle
        if y_position - table_height < 50:
            p.showPage()
            y_position = 750
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y_position, day['date_formatted'] + " (continued)")
            y_position -= 20
        
        table.wrapOn(p, 400, table_height)
        table.drawOn(p, 50, y_position - table_height)
        
        y_position -= table_height + 40
    
    # Finaliser le PDF
    p.showPage()
    p.save()
    
    # Récupérer le PDF depuis le buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Créer la réponse HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="conference_agenda.pdf"'
    return response

# === REGISTRATION VIEWS ===
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Sauvegarde de l'inscription avec session automatique
            registration = form.save()
            
            # Préparation de l'email
            subject = 'Confirmation de votre inscription à Conference 2025'
            html_message = render_to_string('conference_app/email_confirmation.html', {
                'name': registration.name,
                'event_name': 'Conference 2025',
                'session': registration.session,
                'event_date': registration.session.start_date if registration.session else 'À définir',
                'event_location': 'Conference Center',
            })
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = registration.email
            
            # Envoi de l'email
            try:
                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [to_email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f'Inscription réussie pour la session "{registration.session.title}" ! Un email de confirmation vous a été envoyé.')
            except Exception as e:
                messages.success(request, f'Inscription réussie pour la session "{registration.session.title}" !')
                messages.warning(request, 'Cependant, l\'email de confirmation n\'a pas pu être envoyé.')
            
            return redirect('registration_success')
    else:
        form = RegistrationForm()
    
    # Afficher la session courante dans le contexte
    current_session = Session.get_current_session()
    return render(request, 'conference_app/register.html', {
        'form': form,
        'current_session': current_session
    })

def registration_success(request):
    return render(request, 'conference_app/registration_success.html')

# === ATTENDEE VIEWS ===
class AttendeeListView(LoginRequiredMixin, ListView):
    model = Attendee
    template_name = 'conference_app/admin/attendee_list.html'
    context_object_name = 'attendees'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Gestion des inscriptions"
        return context

class AttendeeDetailView(LoginRequiredMixin, DetailView):
    model = Attendee
    template_name = 'conference_app/admin/attendee_detail.html'
    context_object_name = 'attendee'

class AttendeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendee
    form_class = RegistrationForm
    template_name = 'conference_app/admin/attendee_form.html'
    success_url = reverse_lazy('attendee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Inscription mise à jour avec succès.')
        return super().form_valid(form)

@login_required
def delete_attendee(request, pk):
    attendee = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        attendee.delete()
        messages.success(request, f"Registration for {attendee.name} has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

# === ATTENDEE TYPE VIEWS ===
class AttendeeTypeListView(ListView):
    model = AttendeeType
    template_name = 'conference_app/attendee_types.html'
    context_object_name = 'attendee_types'

@login_required
def attendee_type_create(request):
    if request.method == 'POST':
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
        attendee_type.name = request.POST['name']
        attendee_type.description = request.POST['description']
        attendee_type.save()
        messages.success(request, 'Attendee type updated successfully.')
        return redirect('dashboard')
    return render(request, 'admin/attendee_type_form.html', {'attendee_type': attendee_type})

@login_required
def delete_attendee_type(request, pk):
    attendee_type = get_object_or_404(AttendeeType, pk=pk)
    if request.method == 'POST':
        type_name = attendee_type.name
        attendee_type.delete()
        messages.success(request, f"Attendee type '{type_name}' has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

# === PARTNERS VIEWS ===
class PartnerListView(ListView):
    model = Partner
    template_name = 'conference_app/partners.html'
    context_object_name = 'partners'
    queryset = Partner.objects.filter(is_active=True).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Nos Partenaires"
        return context

class PartnerDetailView(DetailView):
    model = Partner
    template_name = 'conference_app/partner_detail.html'
    context_object_name = 'partner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Partenaire - {self.object.name}"
        return context

class PartnerAdminListView(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'conference_app/dashboard/partner_list.html'
    context_object_name = 'partners'
    ordering = ['name']
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Gestion des Partenaires"
        return context

@login_required
def partner_create(request):
    if request.method == 'POST':
        is_active = request.POST.get('is_active') == 'on'
        
        partner = Partner.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            website=request.POST['website'],
            is_active=is_active
        )
        if 'logo' in request.FILES:
            partner.logo = request.FILES['logo']
            partner.save()
        messages.success(request, 'Partner added successfully.')
        return redirect('dashboard')
    return render(request, 'admin/partner_form.html')

@login_required
def partner_edit(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        partner.name = request.POST['name']
        partner.description = request.POST['description']
        partner.website = request.POST['website']
        partner.is_active = request.POST.get('is_active', True) == 'on'
        if 'logo' in request.FILES:
            partner.logo = request.FILES['logo']
        partner.save()
        messages.success(request, 'Partner updated successfully.')
        return redirect('dashboard')
    return render(request, 'admin/partner_form.html', {'partner': partner})

@login_required
def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        partner.delete()
        messages.success(request, 'Partner deleted successfully.')
        return redirect('dashboard')
    return render(request, 'admin/partner_confirm_delete.html', {'partner': partner})

def download_partners_pdf(request):
    partners = Partner.objects.filter(is_active=True).order_by('name')
    
    # Création du PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Titre du document
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(300, 750, "Partenaires de la Conférence")
    pdf.setFont("Helvetica", 12)
    
    y_position = 700  # Position verticale initiale
    
    for partner in partners:
        # Nom du partenaire
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, partner.name)
        y_position -= 20
        
        # Description si elle existe
        if partner.description:
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, y_position, partner.description)
            y_position -= 20
        
        # Site web si il existe
        if partner.website:
            pdf.setFont("Helvetica-Oblique", 12)
            pdf.drawString(50, y_position, f"Site web: {partner.website}")
            y_position -= 20
        
        # Séparateur
        y_position -= 20
        
        # Nouvelle page si nécessaire
        if y_position < 100:
            pdf.showPage()
            y_position = 750
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(300, 750, "Partenaires de la Conférence (suite)")
            pdf.setFont("Helvetica", 12)
    
    # Finalisation du PDF
    pdf.showPage()
    pdf.save()
    
    # Récupération du PDF depuis le buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Création de la réponse HTTP
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="partenaires_conference.pdf"'
    return response

# === SESSION ORGANIZERS VIEWS ===
@login_required
def manage_session_organizers(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    
    if request.method == 'POST':
        if 'add_organizer' in request.POST:
            SessionOrganizer.objects.create(
                session=session,
                name=request.POST['name'],
                organization=request.POST['organization'],
                order=request.POST.get('order', 0),
                is_primary='is_primary' in request.POST
            )
            messages.success(request, "Organizer added successfully.")
        elif 'remove_organizer' in request.POST:
            get_object_or_404(SessionOrganizer, pk=request.POST['organizer_id']).delete()
            messages.success(request, "Organizer removed successfully.")
        return redirect('manage_session_organizers', session_id=session.id)
    
    return render(request, 'conference_app/admin/manage_organizers.html', {
        'session': session,
        'organizers': session.organizers.order_by('order')
    })

class SessionOrganizerUpdateView(LoginRequiredMixin, UpdateView):
    model = SessionOrganizer
    form_class = SessionOrganizerForm
    template_name = 'conference_app/admin/organizer_form.html'
    
    def get_success_url(self):
        return reverse_lazy('session_detail', kwargs={'pk': self.object.session.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Organisateur mis à jour avec succès.')
        return super().form_valid(form)

@login_required
def delete_session_organizer(request, pk):
    organizer = get_object_or_404(SessionOrganizer, pk=pk)
    session_id = organizer.session.id
    if request.method == 'POST':
        organizer.delete()
        messages.success(request, 'Organisateur supprimé avec succès.')
    return redirect('dashboard')

# === SESSION FUNDINGS VIEWS ===
@login_required
def manage_session_fundings(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    
    if request.method == 'POST':
        if 'add_funding' in request.POST:
            SessionFunding.objects.create(
                session=session,
                partner_id=request.POST['partner'],
                funding_type=request.POST['funding_type'],
                description=request.POST['description'],
                amount=request.POST['amount'] or None,
                country=request.POST['country'],
                covers_participants=request.POST.get('covers_participants')
            )
            messages.success(request, "Funding added successfully.")
        elif 'remove_funding' in request.POST:
            get_object_or_404(SessionFunding, pk=request.POST['funding_id']).delete()
            messages.success(request, "Funding removed successfully.")
        return redirect('manage_session_fundings', session_id=session.id)
    
    return render(request, 'conference_app/admin/manage_fundings.html', {
        'session': session,
        'fundings': session.fundings.all(),
        'partners': Partner.objects.filter(is_active=True),
        'funding_types': SessionFunding.FUNDING_TYPES
    })

class SessionFundingUpdateView(LoginRequiredMixin, UpdateView):
    model = SessionFunding
    form_class = SessionFundingForm
    template_name = 'conference_app/admin/funding_form.html'
    
    def get_success_url(self):
        return reverse_lazy('session_detail', kwargs={'pk': self.object.session.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Financement mis à jour avec succès.')
        return super().form_valid(form)

@login_required
def delete_session_funding(request, pk):
    funding = get_object_or_404(SessionFunding, pk=pk)
    session_id = funding.session.id
    if request.method == 'POST':
        funding.delete()
        messages.success(request, 'Financement supprimé avec succès.')
    return redirect('dashboard')

# === INTERVENTION LOCATIONS VIEWS ===
class LocationAdminListView(LoginRequiredMixin, ListView):
    model = InterventionLocation
    template_name = 'conference_app/admin/location_list.html'
    context_object_name = 'locations'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Gestion des lieux d'intervention"
        return context

@login_required
def location_create(request):
    if request.method == 'POST':
        form = InterventionLocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lieu d'intervention ajouté avec succès.")
            return redirect('location_list')
    else:
        form = InterventionLocationForm()
    
    context = {
        'form': form,
        'title': "Ajouter un lieu d'intervention",
    }
    return render(request, 'conference_app/admin/location_form.html', context)

@login_required
def location_edit(request, pk):
    location = get_object_or_404(InterventionLocation, pk=pk)
    if request.method == 'POST':
        form = InterventionLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Lieu d'intervention mis à jour avec succès.")
            return redirect('location_list')
    else:
        form = InterventionLocationForm(instance=location)
    
    context = {
        'form': form,
        'location': location,
        'title': f"Modifier le lieu d'intervention: {location.name}",
    }
    return render(request, 'conference_app/admin/location_form.html', context)

@login_required
def location_delete(request, pk):
    location = get_object_or_404(InterventionLocation, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, "Lieu d'intervention supprimé avec succès.")
        return redirect('location_list')
    
    context = {
        'location': location,
        'title': f"Supprimer le lieu d'intervention: {location.name}",
    }
    return render(request, 'conference_app/admin/location_confirm_delete.html', context)

@login_required
def manage_intervention_locations(request):
    if request.method == 'POST':
        if 'add_location' in request.POST:
            InterventionLocation.objects.create(
                name=request.POST['name'],
                country=request.POST['country'],
                is_primary='is_primary' in request.POST
            )
            messages.success(request, "Location added successfully.")
        elif 'remove_location' in request.POST:
            get_object_or_404(InterventionLocation, pk=request.POST['location_id']).delete()
            messages.success(request, "Location removed successfully.")
        return redirect('dashboard')
    
    return render(request, 'admin/location_form.html', {
        'locations': InterventionLocation.objects.all()
    })

@login_required
def delete_intervention_location(request, pk):
    location = get_object_or_404(InterventionLocation, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, f"Lieu d'intervention '{location.name}' supprimé avec succès.")
        return redirect('location_list')
    return redirect('location_list')

# === DASHBOARD VIEW ===
@login_required
def dashboard_view(request):
    partner_count = Partner.objects.count()
    active_partners = Partner.objects.filter(is_active=True).count()
    recent_partners = Partner.objects.order_by('-created_at')[:6]
    
    context = {
        'total_registrations': Attendee.objects.count(),
        'total_sessions': Session.objects.count(),
        'total_speakers': SpeakersInterventions.objects.count(),
        'recent_registrations': Attendee.objects.all().order_by('-registration_date')[:10],
        
        'speakers': SpeakersInterventions.objects.all(),
        'sessions': Session.objects.all().order_by('start_date'),
        'agenda_items': AgendaItem.objects.all().order_by('date', 'start_time'),
        'attendee_types': AttendeeType.objects.all(),

        'partner_count': partner_count,
        'active_partners': active_partners,
        'recent_partners': recent_partners,
        'partners': Partner.objects.all(),
        
        # New stats
        'total_locations': InterventionLocation.objects.count(),
        'hybrid_sessions': Session.objects.filter(is_hybrid=True).count(),
        'total_fundings': SessionFunding.objects.count(),
        
        'page_title': "Tableau de bord Administrateur"
    }

    return render(request, 'conference_app/dashboard.html', context)

# === OTHER VIEWS ===
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Récupération des données du formulaire
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Construction du message
            full_message = f"""
            Nouveau message de contact:
            
            De: {name} <{email}>
            Sujet: {subject}
            
            Message:
            {message}
            """
            
            try:
                # Envoi de l'email
                send_mail(
                    subject=f"Message de contact: {subject}",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                
                # Message de succès
                messages.success(request, "Votre message a bien été envoyé ! Nous vous répondrons dès que possible.")
                return redirect('contact')  # Redirige vers la même page contact
                
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de l'envoi du message. Veuillez réessayer. Erreur: {str(e)}")
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

def subscribe(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Merci pour votre abonnement !')
            return redirect('home')  # Redirige vers la page d'accueil
    else:
        form = SubscribeForm()
    
    return render(request, 'votre_template.html', {'form': form})