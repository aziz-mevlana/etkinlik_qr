from django.contrib import admin
from .models import Ticket, Yoklama, AktifOturum


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'department', 'qr_code', 'toplam_katilim')
    list_filter = ('department',)
    search_fields = ('name', 'student_id')
    list_per_page = 20


@admin.register(Yoklama)
class YoklamaAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'oturum', 'tarih')
    list_filter = ('oturum',)
    search_fields = ('ticket__name', 'ticket__student_id')
    list_per_page = 20


@admin.register(AktifOturum)
class AktifOturumAdmin(admin.ModelAdmin):
    list_display = ('oturum',)
