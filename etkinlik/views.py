import io, base64, qrcode, uuid
import json
import os
import csv
from functools import wraps
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket, Yoklama, AktifOturum
from django.shortcuts import render, get_object_or_404
from .forms import KatilimForm
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout

OTURUM_ISIMLERI = {
    1: "Gün 1 - Oturum 1",
    2: "Gün 1 - Oturum 2",
    3: "Gün 2 - Oturum 1",
    4: "Gün 2 - Oturum 2",
    5: "Gün 3 - Oturum 1",
    6: "Gün 3 - Oturum 2",
}


def gorevli_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/etkinlik/giris/')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        if request.user.groups.filter(name='Görevli').exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('etkinlik_katilim') + '?yetki=yok')
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/etkinlik/giris/')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('etkinlik_katilim') + '?yetki=yok')
    return wrapper


def giris(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', reverse('qr_tarayici'))
        return HttpResponseRedirect(next_url)
    hata = None
    if request.method == 'POST':
        kullanici_adi = request.POST.get('kullanici_adi')
        sifre = request.POST.get('sifre')
        user = authenticate(request, username=kullanici_adi, password=sifre)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', reverse('qr_tarayici'))
            return HttpResponseRedirect(next_url)
        else:
            hata = 'Kullanıcı adı veya şifre hatalı.'
    return render(request, 'etkinlik/giris.html', {'hata': hata})


def cikis(request):
    logout(request)
    return HttpResponseRedirect(reverse('giris'))


def generate_qr_image(qr_data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def etkinlik_katilim(request):
    if request.GET.get('yetki') == 'yok':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('giris'))

    qr_img = None
    ticket = None
    if request.method == "POST":
        form = KatilimForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                ticket = Ticket.objects.get(
                    name=data['name'],
                    student_id=data['student_id'],
                    department=data['department']
                )
                qr_img = generate_qr_image(ticket.qr_code)
            except Ticket.DoesNotExist:
                ticket = Ticket(
                    name=data['name'],
                    student_id=data['student_id'],
                    department=data['department']
                )
                ticket.save()
                qr_img = generate_qr_image(ticket.qr_code)
    else:
        form = KatilimForm()

    is_gorevli = request.user.is_authenticated and (
        request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name='Görevli').exists()
    )
    return render(request, "etkinlik/katilim_form.html", {
        "form": form,
        "qr_img": qr_img,
        "is_gorevli": is_gorevli,
        "ticket": ticket,
    })


def ogrenci_sorgulama(request):
    ticket = None
    yoklamalar = []
    hata = None
    qr_img = None

    if request.method == "POST":
        student_id = request.POST.get('student_id', '').strip()
        if student_id:
            try:
                ticket = Ticket.objects.get(student_id=student_id)
                qr_img = generate_qr_image(ticket.qr_code)
                katildigi = ticket.katildigi_oturumlar()
                for oturum_no, oturum_adi in OTURUM_ISIMLERI.items():
                    yoklamalar.append({
                        'oturum_no': oturum_no,
                        'oturum_adi': oturum_adi,
                        'katildi': oturum_no in katildigi,
                    })
            except Ticket.DoesNotExist:
                hata = 'Bu öğrenci numarasına ait kayıt bulunamadı.'
        else:
            hata = 'Lütfen öğrenci numaranızı girin.'

    return render(request, "etkinlik/ogrenci_sorgulama.html", {
        "ticket": ticket,
        "yoklamalar": yoklamalar,
        "hata": hata,
        "qr_img": qr_img,
    })


@gorevli_required
def qr_kod_onayla(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            oturum = int(data.get('oturum', 0))

            if oturum < 1 or oturum > 6:
                return JsonResponse({'status': 'error', 'message': 'Geçersiz oturum seçimi.'})

            ticket = Ticket.objects.get(qr_code=qr_data)

            if Yoklama.objects.filter(ticket=ticket, oturum=oturum).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'{ticket.name} bu oturumda zaten yoklama almış.',
                    'owner': f'{ticket.name}, {ticket.student_id}'
                })

            Yoklama.objects.create(ticket=ticket, oturum=oturum)

            return JsonResponse({
                'status': 'success',
                'message': f'Yoklama alındı - {OTURUM_ISIMLERI[oturum]}',
                'owner': f'{ticket.name}, {ticket.student_id}'
            })
        except Ticket.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz QR kod.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Yalnızca POST isteği kabul edilir.'})


@gorevli_required
def qr_tarayici(request):
    aktif = AktifOturum.get_aktif()
    return render(request, "etkinlik/qr_tarayici.html", {
        "oturumlar": OTURUM_ISIMLERI,
        "aktif_oturum": aktif,
        "aktif_oturum_adi": OTURUM_ISIMLERI.get(aktif, "Bilinmiyor"),
    })


@admin_required
def katilimci_listesi(request):
    tickets = Ticket.objects.all().order_by('name')
    tum_yoklamalar = Yoklama.objects.select_related('ticket').all()

    yoklama_durumu = {}
    for y in tum_yoklamalar:
        if y.ticket_id not in yoklama_durumu:
            yoklama_durumu[y.ticket_id] = set()
        yoklama_durumu[y.ticket_id].add(y.oturum)

    katilim_listesi = []
    for ticket in tickets:
        katildigi = yoklama_durumu.get(ticket.id, set())
        katilim_listesi.append({
            'ticket': ticket,
            'oturumlar': [o in katildigi for o in range(1, 7)],
            'toplam': len(katildigi),
        })

    toplam_katilimci = tickets.count()

    is_gorevli = request.user.is_authenticated and (
        request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name='Görevli').exists()
    )
    aktif = AktifOturum.get_aktif()
    return render(request, "etkinlik/katilimci_listesi.html", {
        "katilim_listesi": katilim_listesi,
        "toplam_katilimci": toplam_katilimci,
        "oturum_isimleri": OTURUM_ISIMLERI,
        "form": KatilimForm(),
        "is_gorevli": is_gorevli,
        "aktif_oturum": aktif,
    })


@admin_required
def csv_indir(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="katilimci_listesi.csv"'

    writer = csv.writer(response)
    header = ['Ad', 'Öğrenci Numarası', 'Bölüm']
    for o in range(1, 7):
        header.append(OTURUM_ISIMLERI[o])
    header.append('Toplam')
    writer.writerow(header)

    tickets = Ticket.objects.all().order_by('student_id')
    tum_yoklamalar = Yoklama.objects.select_related('ticket').all()

    yoklama_durumu = {}
    for y in tum_yoklamalar:
        if y.ticket_id not in yoklama_durumu:
            yoklama_durumu[y.ticket_id] = set()
        yoklama_durumu[y.ticket_id].add(y.oturum)

    for ticket in tickets:
        katildigi = yoklama_durumu.get(ticket.id, set())
        row = [ticket.name, ticket.student_id, ticket.get_department_display()]
        for o in range(1, 7):
            row.append('+' if o in katildigi else '-')
        row.append(len(katildigi))
        writer.writerow(row)

    return response


@admin_required
def katilimci_ekle(request):
    if request.method == "POST":
        form = KatilimForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Ticket.objects.get_or_create(
                student_id=data['student_id'],
                defaults={
                    'name': data['name'],
                    'department': data['department'],
                }
            )
    return HttpResponseRedirect(reverse("katilimci_listesi"))


@admin_required
def katilimci_sil(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.delete()
    return HttpResponseRedirect(reverse("katilimci_listesi"))


@admin_required
def tum_katilimcilari_sil(request):
    if request.method == 'POST':
        Yoklama.objects.all().delete()
        Ticket.objects.all().delete()
        return HttpResponseRedirect(reverse("katilimci_listesi"))
    return HttpResponseRedirect(reverse("katilimci_listesi"))


@admin_required
def aktif_oturum_degistir(request):
    if request.method == 'POST':
        oturum = int(request.POST.get('oturum', 1))
        if 1 <= oturum <= 6:
            AktifOturum.objects.update_or_create(
                pk=1,
                defaults={'oturum': oturum}
            )
    return HttpResponseRedirect(reverse("katilimci_listesi"))
