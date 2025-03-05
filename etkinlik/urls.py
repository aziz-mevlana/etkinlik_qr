from django.urls import path
from . import views

urlpatterns = [
    path('katilim/', views.etkinlik_katilim, name='etkinlik_katilim'),
    path('', views.etkinlik_katilim, name='etkinlik_katilim'),
    path('qr-onayla/', views.qr_kod_onayla, name='qr_kod_onayla'),
    path('qr-tarayici/', views.qr_tarayici, name='qr_tarayici'),
    path('katilimci-listesi/', views.katilimci_listesi, name='katilimci_listesi'),
    path('katilimci-ekle/', views.katilimci_ekle, name='katilimci_ekle'),
    path('katilimci-sil/<int:ticket_id>/', views.katilimci_sil, name='katilimci_sil'),
    path('katilimci-katildi/<int:ticket_id>/', views.katilimci_katildi, name='katilimci_katildi'),
]