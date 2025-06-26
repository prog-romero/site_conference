
from django import forms
from .models import (
    Session, SpeakersInterventions, AgendaItem, AttendeeType, Attendee, 
    Partner, InterventionLocation, SessionFunding, SessionOrganizer,
    MenuPhoto, StudentVolunteer
)
import pycountry

# ============================================================================
# AGENDA FORMS - Formulaires pour la gestion de l'agenda
# ============================================================================

class AgendaItemForm(forms.ModelForm):
    class Meta:
        model = AgendaItem
        # ▼▼▼▼ CHAMP 'speaker_intervention' AJOUTÉ ▼▼▼▼
        fields = ['title', 'description', 'date', 'start_time', 'end_time', 'item_type', 'location', 'speaker_intervention']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            # ▼▼▼▼ WIDGET POUR LE NOUVEAU CHAMP ▼▼▼▼
            'speaker_intervention': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        # Limiter les choix de speaker_intervention à ceux de la session actuelle
        if self.session:
            self.fields['speaker_intervention'].queryset = SpeakersInterventions.objects.filter(session=self.session)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        session = self.session or (self.instance.session if self.instance.pk else None)

        if session and date:
            if date < session.start_date or date > session.end_date:
                self.add_error('date', f'The date must be between {session.start_date.strftime("%d %B %Y")} and {session.end_date.strftime("%d %B %Y")}.')

        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'The end time must be after the start time.')

        return cleaned_data

# ============================================================================
# ATTENDEE FORMS - Formulaires pour la gestion des participants
# ============================================================================

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['name', 'email', 'company', 'job_title', 'attendee_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'attendee_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        self.fields['name'].label = "Nom complet"
        self.fields['email'].label = "Adresse email"
        self.fields['company'].label = "Entreprise (facultatif)"

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email and Attendee.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.add_error('email', 'Cet email est déjà utilisé.')
        return cleaned_data

class AttendeeTypeForm(forms.ModelForm):
    class Meta:
        model = AttendeeType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# ============================================================================
# CONTACT FORMS - Formulaires de contact et communication
# ============================================================================

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

# ============================================================================
# LOCATION FORMS - Formulaires pour la gestion des lieux
# ============================================================================

class InterventionLocationForm(forms.ModelForm):
    COUNTRY_CHOICES = [(country.alpha_2, country.name) for country in pycountry.countries]
    
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
    )

    class Meta:
        model = InterventionLocation
        fields = ['name', 'country', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ============================================================================
# PARTNER FORMS - Formulaires pour la gestion des partenaires
# ============================================================================

class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'logo', 'website', 'description', 'is_active', 'partner_type', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'partner_type': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ============================================================================
# REGISTRATION FORMS - Formulaires d'inscription
# ============================================================================

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['name', 'email', 'company', 'job_title', 'attendee_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'attendee_type': forms.Select(attrs={'class': 'form-select'}),
        }

# ============================================================================
# SESSION FORMS - Formulaires pour la gestion des sessions
# ============================================================================

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'title', 'description', 'logo', 'start_date', 'end_date', 
            'track', 'location', 'locations', 'is_hybrid'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'track': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'locations': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_hybrid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'duration_days' in self.fields:
            self.fields['duration_days'].widget.attrs['readonly'] = True

class SessionFundingForm(forms.ModelForm):
    class Meta:
        model = SessionFunding
        fields = ['partner', 'funding_type', 'description', 'amount', 'country']
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-select'}),
            'funding_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SessionOrganizerForm(forms.ModelForm):
    class Meta:
        model = SessionOrganizer
        fields = ['name', 'organization', 'order', 'is_primary', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
# ============================================================================
# SPEAKER FORMS - Formulaires pour la gestion des intervenants
# ============================================================================

class SpeakersInterventionsForm(forms.ModelForm):
    class Meta:
        model = SpeakersInterventions
        # ▼▼▼▼ NOUVEAUX CHAMPS 'slides_file' ET 'slides_status' AJOUTÉS ▼▼▼▼
        fields = [
            'name', 'title', 'organization', 'intervention_type', 'photo', 
            'session', 'slides_file', 'slides_status'
        ]
        widgets = {
            'session': forms.HiddenInput(),
            # ▼▼▼▼ WIDGETS POUR LES NOUVEAUX CHAMPS ▼▼▼▼
            'slides_file': forms.FileInput(attrs={'class': 'form-control'}),
            'slides_status': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'intervention_type': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        if session:
            self.fields['session'].initial = session
            self.fields['session'].disabled = True




# ============================================================================
# SUBSCRIPTION FORMS - Formulaires d'abonnement
# ============================================================================

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'})
        }

# ============================================================================
# GALLERY & VOLUNTEER FORMS - NOUVEAUX FORMULAIRES AJOUTÉS
# ============================================================================
# conference_app/forms.py

class MenuPhotoForm(forms.ModelForm):
    """
    Formulaire pour téléverser et gérer une photo de la galerie.
    """
    class Meta:
        model = MenuPhoto
        # ▼▼▼▼ 'date' AJOUTÉ À LA LISTE DES CHAMPS ▼▼▼▼
        fields = ['photo', 'date', 'caption', 'description', 'order']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'required': True}),
            # ▼▼▼▼ WIDGET POUR LE NOUVEAU CHAMP 'date' ▼▼▼▼
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date', # Utilise le sélecteur de date du navigateur
                }
            ),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cérémonie d\'ouverture'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description détaillée de la photo (optionnel)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }

class StudentVolunteerForm(forms.ModelForm):
    """
    Formulaire pour ajouter ou modifier un étudiant volontaire.
    """
    class Meta:
        model = StudentVolunteer
        fields = ['full_name', 'institute', 'role', 'photo', 'order']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'institute': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Accueil, Support Technique'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }
