from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Session, SpeakersInterventions, AgendaItem, AttendeeType, Attendee, 
    Partner, InterventionLocation, SessionFunding, SessionOrganizer
)

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

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'})
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'track', 'locations', 'is_hybrid'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'track': forms.Select(attrs={'class': 'form-select'}),
            'locations': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_hybrid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SpeakersInterventionsForm(forms.ModelForm):
    class Meta:
        model = SpeakersInterventions
        fields = [
            'name', 'title', 'organization', 'bio', 'photo', 'gender',
            'session', 'intervention_type', 'location', 'is_remote',
            'countries'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
            'intervention_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'countries': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Ajoute ici d'autres vérifications si besoin, par exemple en fonction du type d'intervention
        return cleaned_data

class AgendaItemForm(forms.ModelForm):
    class Meta:
        model = AgendaItem
        fields = [
            'title', 'description', 'date', 'start_time', 'end_time',
            'item_type', 'location', 'session'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Validate start_time <= end_time
        if start_time and end_time and start_time > end_time:
            raise ValidationError("The start time must be before or equal to the end time.")
        
        # Call model's clean method for session date validation
        instance = self.instance or AgendaItem(**cleaned_data)
        instance.clean()
        return cleaned_data

class AttendeeTypeForm(forms.ModelForm):
    class Meta:
        model = AttendeeType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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

class InterventionLocationForm(forms.ModelForm):
    class Meta:
        model = InterventionLocation
        fields = ['name', 'country', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SessionOrganizerForm(forms.ModelForm):
    class Meta:
        model = SessionOrganizer
        fields = ['name', 'organization', 'order', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
