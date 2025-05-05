import io, base64, qrcode, uuid
import json
import os
import csv
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket
from django.shortcuts import render, get_object_or_404
from .forms import KatilimForm
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required

def get_day_number():
    # Etkinliğin başlangıç tarihi (6 Haziran 2024)
    start_date = datetime(2024, 6, 6)
    today = datetime.now()
    day_diff = (today - start_date).days + 1
    
    # Eğer etkinlik günleri dışındaysa veya 3 günden fazlaysa None döndür
    if day_diff < 1 or day_diff > 3:
        return None
    return day_diff

def log_yoklama(ticket, is_entry):
    day_number = get_day_number()
    if day_number is None:
        return  # Etkinlik günleri dışında log tutma
    
    log_dir = os.path.join(settings.BASE_DIR, 'etkinlik', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Gün numarasına göre dosya adı oluştur
    log_file = os.path.join(log_dir, f'yoklama_log_gun_{day_number}.txt')
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timezone.now()} - {ticket.name} - {ticket.student_id} - {ticket.department} - {'Giriş' if is_entry else 'Çıkış'}\n")

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/admin/login/?next=' + request.path)
        return view_func(request, *args, **kwargs)
    return wrapper

def etkinlik_katilim(request):
    qr_img = None
    if request.method == "POST":
        form = KatilimForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Kullanıcının zaten bir bileti olup olmadığını kontrol et
            try:
                ticket = Ticket.objects.get(name=data['name'], student_id=data['student_id'], department=data['department'])
                qr_data = ticket.qr_code
            except Ticket.DoesNotExist:
                unique_id = str(uuid.uuid4())
                qr_data = f"Ad: {data['name']}, Öğrenci-Numarası: {data['student_id']}, Bölüm: {data['department']}, ID: {unique_id}"
                
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
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                qr_img = img_base64
                
                # Bilet bilgilerini kaydet
                Ticket.objects.create(name=data['name'], student_id=data['student_id'], department=data['department'], qr_code=qr_data)
            else:
                # Mevcut QR kodunu base64 formatına çevir
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
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                qr_img = img_base64
        else:
            pass
            
    else:
        form = KatilimForm()
            
    return render(request, "etkinlik/katilim_form.html", {"form": form, "qr_img": qr_img})

@login_required
def qr_kod_onayla(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            
            # Veritabanında QR kodu eşleşen bileti bulmaya çalışıyoruz.
            ticket = Ticket.objects.get(qr_code=qr_data)
            
            # Eğer kişi çıkış yapmışsa tekrar giriş yapabilir
            if ticket.is_joined and ticket.leave_date is None:
                return JsonResponse({'status': 'error', 'message': 'Bu bilet zaten kullanılmış.'})
            
            # Katılım onaylama işlemi
            ticket.is_joined = True
            current_time = timezone.now()
            ticket.entry_date = current_time
            ticket.leave_date = None  # Çıkış tarihini sıfırla
            ticket.save()
            
            # Loglama işlemi
            log_yoklama(ticket, is_entry=True)
            
            return JsonResponse({'status': 'success'})
        except Ticket.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz QR kod.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Yalnızca POST isteği kabul edilir.'})

@login_required
def qr_cikis_onayla(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            
            # Veritabanında QR kodu eşleşen bileti bulmaya çalışıyoruz.
            ticket = Ticket.objects.get(qr_code=qr_data)
            
            if not ticket.is_joined:
                return JsonResponse({'status': 'error', 'message': 'Bu bilet henüz kullanılmamış.'})
            
            if ticket.leave_date is not None:
                return JsonResponse({'status': 'error', 'message': 'Bu bilet için zaten çıkış yapılmış.'})
            
            # Çıkış onaylama işlemi
            current_time = timezone.now()
            ticket.leave_date = current_time
            ticket.save()
            
            # Loglama işlemi
            log_yoklama(ticket, is_entry=False)
            
            return JsonResponse({'status': 'success'})
        except Ticket.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz QR kod.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Yalnızca POST isteği kabul edilir.'})

@login_required
def qr_tarayici(request):
    return render(request, "etkinlik/qr_tarayici.html")

@login_required
def katilimci_listesi(request):
    katilanlar = Ticket.objects.filter(is_joined=True)
    katilmayanlar = Ticket.objects.filter(is_joined=False)
    toplam_katilimci = (katilanlar.count() + katilmayanlar.count())
    return render(request, "etkinlik/katilimci_listesi.html", {"katilanlar": katilanlar, "katilmayanlar": katilmayanlar, "toplam_katilimci":toplam_katilimci, "form": KatilimForm()})

@login_required
def csv_indir(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="katilimci_listesi.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Ad', 'Öğrenci Numarası', 'Bölüm', 'Giriş Tarihi', 'Çıkış Tarihi'])
    
    katilanlar = Ticket.objects.filter(is_joined=True)
    for katilimci in katilanlar:
        writer.writerow([
            katilimci.name,
            katilimci.student_id,
            katilimci.get_department_display(),
            katilimci.entry_date.strftime('%Y-%m-%d %H:%M:%S') if katilimci.entry_date else '-',
            katilimci.leave_date.strftime('%Y-%m-%d %H:%M:%S') if katilimci.leave_date else '-'
        ])
    
    return response

@login_required
def katilimcilari_sifirla(request):
    if request.method == 'POST':
        # Tüm katılımcıların katılım durumunu sıfırla
        Ticket.objects.all().update(
            is_joined=False,
            entry_date=None,
            leave_date=None
        )
        return HttpResponseRedirect(reverse("katilimci_listesi"))
    return HttpResponseRedirect(reverse("katilimci_listesi"))

@login_required
def katilimci_ekle(request):
    if request.method == "POST":
        form = KatilimForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Ticket.objects.create(name=data['name'], student_id=data['student_id'], department=data['department'], qr_code="")
    return HttpResponseRedirect(reverse("katilimci_listesi"))

@login_required
def katilimci_sil(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.delete()
    return HttpResponseRedirect(reverse("katilimci_listesi"))

@login_required
def katilimci_katildi(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.is_joined = True
    ticket.entry_date = timezone.now()
    ticket.save()
    return HttpResponseRedirect(reverse("katilimci_listesi"))


