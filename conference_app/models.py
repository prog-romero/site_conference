from django.db import models
from django.utils import timezone
from django.db.models import Count

class AttendeeType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
class InterventionLocation(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name}, {self.country}"

class Session(models.Model):
    TRACK_CHOICES = [
        ('technical', 'Technical'),
        ('business', 'Business'),
        ('workshop', 'Workshop'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Uniquement des dates, pas d'heures
    start_date = models.DateField()
    end_date = models.DateField()
    track = models.CharField(max_length=20, choices=TRACK_CHOICES)
    # Garder location comme champ de texte pour compatibilité
    location = models.CharField(max_length=100, blank=True, null=True)
    locations = models.ManyToManyField(InterventionLocation, related_name='sessions', blank=True)
    is_hybrid = models.BooleanField(default=False)
    duration_days = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Calculer automatiquement duration_days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.duration_days = delta.days + 1
        super().save(*args, **kwargs)

    @classmethod
    def get_current_session(cls):
        """Retourne la session la plus récente (actuelle)"""
        today = timezone.now().date()
        # D'abord, chercher une session en cours
        current_session = cls.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
        
        if current_session:
            return current_session
            
        # Sinon, retourner la prochaine session
        upcoming_session = cls.objects.filter(
            start_date__gt=today
        ).order_by('start_date').first()
        
        if upcoming_session:
            return upcoming_session
            
        # En dernier recours, retourner la session la plus récente
        return cls.objects.order_by('-start_date').first()

class SpeakersInterventions(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    INTERVENTION_TYPES = [
        ('presentation', 'Presentation'),
        ('keynote', 'Keynote'),
        ('panel', 'Panel Discussion'),
        ('moderation', 'Moderation'),
        ('workshop', 'Workshop'),
    ]
    
    # Attributs de base du speaker
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='speakers/', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    
    # Attributs liés à l'intervention
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='speakers')
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPES)
    location = models.ForeignKey(InterventionLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='speakers')
    is_remote = models.BooleanField(default=False)
    
    # Autres attributs
    countries = models.ManyToManyField(InterventionLocation, blank=True, related_name='speaker_countries')

    class Meta:
        unique_together = ('name', 'session')
        verbose_name = "Speaker Intervention"
        verbose_name_plural = "Speakers Interventions"

    def __str__(self):
        return f"{self.name} - {self.session.title} ({self.get_intervention_type_display()})"

class AgendaItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('break', 'Break'),
        ('lunch', 'Lunch'),
        ('keynote', 'Keynote'),
        ('registration', 'Registration'),
        ('networking', 'Networking'),
        ('session', 'Session'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    location = models.ForeignKey(InterventionLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='agenda_items')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, blank=True, null=True, related_name='agenda_items')
    speaker = models.ForeignKey(SpeakersInterventions, on_delete=models.SET_NULL, blank=True, null=True, related_name='agenda_items')
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.start_time}"
    
    def clean(self):
        # Vérifier que la date de l'agenda est dans la période de la session
        if self.session and self.date:
            if self.date < self.session.start_date or self.date > self.session.end_date:
                from django.core.exceptions import ValidationError
                raise ValidationError("La date de l'agenda doit être dans la période de la session")

class Attendee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    attendee_type = models.ForeignKey(AttendeeType, on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendees', null=True, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('email', 'session')
    
    def __str__(self):
        return f"{self.name} - {self.email} ({self.session.title if self.session else 'No session'})"
    
    def save(self, *args, **kwargs):
        # Auto-assigner la session courante si aucune session n'est spécifiée
        if not self.session_id:
            self.session = Session.get_current_session()
        super().save(*args, **kwargs)
    
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Partner(models.Model):
    PARTNER_TYPES = [
        ('academic', 'Academic'),
        ('corporate', 'Corporate'),
        ('government', 'Government'),
        ('ngo', 'Non-Profit'),
    ]
    
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default='corporate')
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class SessionOrganizer(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='organizers')
    name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.organization})"

class SessionFunding(models.Model):
    FUNDING_TYPES = [
        ('mission', 'Mission'),
        ('equipment', 'Equipment'),
        ('banquet', 'Banquet'),
        ('other', 'Other'),
    ]
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='fundings')
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE, related_name='fundings')
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    covers_participants = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.partner.name} - {self.get_funding_type_display()}"