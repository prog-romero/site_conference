from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Speaker, Session, AgendaItem, AttendeeType, Attendee, Partner
from .forms import RegistrationForm, ContactForm
from django.db.models import Q
from datetime import datetime
from .forms import SubscribeForm, PartnerForm

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
from .models import Attendee, Speaker, Session, AgendaItem, AttendeeType
from django.utils import timezone



def home(request):
    featured_speakers = Speaker.objects.all()[:4]
    upcoming_sessions = Session.objects.filter(date__gte=timezone.now().date()).order_by('date', 'start_time')[:5]
    latest_session = Session.objects.filter(date__gte=timezone.now().date()).order_by('date', 'start_time').first()
    attendee_types = AttendeeType.objects.all()
    partners = Partner.objects.filter(is_active=True).order_by('name')  # Récupération des partenaires actifs
    
    context = {
        'featured_speakers': featured_speakers,
        'upcoming_sessions': upcoming_sessions,
        'attendee_types': attendee_types,
        'partners': partners,  # Ajout des partenaires au contexte
        'latest_session': latest_session,
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

def agenda_view(request):
    # Récupérez les jours et les éléments d'agenda depuis la base de données
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
    
    context = {
        'agenda_days': agenda_days
    }
    return render(request, 'conference_app/agenda.html', context)

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
            
            data.append([
                time_str,
                item.title,
                item.get_item_type_display(),
                item.location or ""
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


# Ajout des nouvelles vues pour les partenaires
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

# Vue pour le téléchargement du PDF des partenaires
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



# === Partenaires dans le dashboard ===

class PartnerAdminListView(ListView):
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
def dashboard_view(request):

    partner_count = Partner.objects.count()
    active_partners = Partner.objects.filter(is_active=True).count()
    recent_partners = Partner.objects.order_by('-created_at')[:6]
    context = {
        'total_registrations': Attendee.objects.count(),
        'total_sessions': Session.objects.count(),
        'total_speakers': Speaker.objects.count(),
        'recent_registrations': Attendee.objects.all().order_by('-registration_date')[:10],
        'speakers': Speaker.objects.all(),
        'sessions': Session.objects.all().order_by('date', 'start_time'),
        'agenda_items': AgendaItem.objects.all().order_by('date', 'start_time'),
        'attendee_types': AttendeeType.objects.all(),

        'partner_count': partner_count,
        'active_partners': active_partners,
        'recent_partners': recent_partners,
        'partners': Partner.objects.all(),
        'page_title': "Tableau de bord Administrateur"
    }

    return render(request, 'conference_app/dashboard.html', context)



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




@login_required
def partner_create(request):
    if request.method == 'POST':

        is_active = request.POST.get('is_active') == 'on'
        
        # Handle form submission
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

        
        # Handle form submission
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
# Vue pour supprimer un participant (Attendee)
@login_required
def delete_attendee(request, pk):
    attendee = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        attendee.delete()
        messages.success(request, f"Registration for {attendee.name} has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

# Vue pour supprimer un speaker
@login_required
def delete_speaker(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    if request.method == 'POST':
        speaker_name = speaker.name
        speaker.delete()
        messages.success(request, f"Speaker {speaker_name} has been deleted successfully.")
        return redirect('dashboard')
    
# Vue pour supprimer une session
@login_required
def delete_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        session_title = session.title
        session.delete()
        messages.success(request, f"Session '{session_title}' has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

# Vue pour supprimer un élément d'agenda
@login_required
def delete_agenda_item(request, pk):
    agenda_item = get_object_or_404(AgendaItem, pk=pk)
    if request.method == 'POST':
        item_title = agenda_item.title
        agenda_item.delete()
        messages.success(request, f"Agenda item '{item_title}' has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

# Vue pour supprimer un type de participant
@login_required
def delete_attendee_type(request, pk):
    attendee_type = get_object_or_404(AttendeeType, pk=pk)
    if request.method == 'POST':
        type_name = attendee_type.name
        attendee_type.delete()
        messages.success(request, f"Attendee type '{type_name}' has been deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')
