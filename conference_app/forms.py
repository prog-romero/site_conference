from django import forms
from .models import (
    Session, SpeakersInterventions, AgendaItem, AttendeeType, Attendee, 
    Partner, InterventionLocation, SessionFunding, SessionOrganizer
)
import pycountry

# ============================================================================
# AGENDA FORMS - Formulaires pour la gestion de l'agenda
# ============================================================================

class AgendaItemForm(forms.ModelForm):
    class Meta:
        model = AgendaItem
        fields = ['title', 'description', 'date', 'start_time', 'end_time', 'item_type', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        session = self.session or (self.instance.session if self.instance.pk else None)

        if session and date:
            if date < session.start_date or date > session.end_date:
                self.add_error('date', f'La date doit être entre {session.start_date.strftime("%d %B %Y")} et {session.end_date.strftime("%d %B %Y")}.')

        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'L’heure de fin doit être postérieure à l’heure de début.')

        return cleaned_data

# ============================================================================
# ATTENDEE FORMS - Formulaires pour la gestion des participants
# ============================================================================

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['name', 'email', 'company']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
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
    # Définir les choix pour le champ country
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
            'is_primary': forms.CheckboxInput(),
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
            'title', 'description', 'start_date', 'end_date', 
            'track', 'location', 'locations', 'is_hybrid'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'track': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'locations': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_hybrid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make duration_days read-only if needed (optional)
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
        fields = ['name', 'title', 'organization', 'intervention_type', 'photo', 'session']
        widgets = {
            'session': forms.HiddenInput(),  # Rendre le champ caché
        }

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        if session:
            self.fields['session'].initial = session  # Définir la session par défaut
            self.fields['session'].disabled = True  # Empêcher la modification

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