from django.contrib import admin
from .models import Ticket

admin.site.register(Ticket)

class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'department', 'is_joined', 'entry_date')
    list_filter = ('is_joined', 'department')
    search_fields = ('name', 'student_id')
    list_per_page = 20