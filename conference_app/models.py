from django.db import models
from django.utils import timezone

class AttendeeType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Speaker(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='speakers/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Session(models.Model):
    TRACK_CHOICES = [
        ('technical', 'Technical'),
        ('business', 'Business'),
        ('workshop', 'Workshop'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    track = models.CharField(max_length=20, choices=TRACK_CHOICES)
    location = models.CharField(max_length=100)
    speakers = models.ManyToManyField(Speaker, related_name='sessions')
    
    def __str__(self):
        return self.title

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
    location = models.CharField(max_length=100, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, blank=True, null=True, related_name='agenda_items')
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.start_time}"

class Attendee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    attendee_type = models.ForeignKey(AttendeeType, on_delete=models.SET_NULL, null=True)
    registration_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} - {self.email}"