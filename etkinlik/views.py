import io, base64, qrcode, uuid
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket
from django.shortcuts import render, get_object_or_404
from .forms import KatilimForm
from django.urls import reverse
from django.utils import timezone

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
            
            if ticket.is_joined:
                return JsonResponse({'status': 'error', 'message': 'Bu bilet zaten kullanılmış.'})
            
            # Katılım onaylama işlemi
            ticket.is_joined = True
            current_time = timezone.now()
            if ticket.entry_date is None:
                ticket.entry_date = current_time
            else:
                pass
            ticket.save()
            
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
            
            # Çıkış onaylama işlemi
            current_time = timezone.now()
            ticket.leave_date = current_time
            ticket.save()
            
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


