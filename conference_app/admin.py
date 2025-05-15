from django.contrib import admin
from .models import Speaker, Session, AgendaItem, Attendee, AttendeeType

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'organization')
    search_fields = ('name', 'organization')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'end_time')
    list_filter = ('date', 'track')
    search_fields = ('title', 'description')
    filter_horizontal = ('speakers',)

@admin.register(AgendaItem)
class AgendaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'end_time', 'item_type')
    list_filter = ('date', 'item_type')
    search_fields = ('title', 'description')

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'registration_date')
    list_filter = ('attendee_type', 'registration_date')
    search_fields = ('name', 'email', 'company')

@admin.register(AttendeeType)
class AttendeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')