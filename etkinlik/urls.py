from django.urls import path
from . import views

urlpatterns = [
    path('', views.etkinlik_katilim, name='etkinlik_katilim'),
    path('qr-onayla/', views.qr_kod_onayla, name='qr_kod_onayla'),
    path('qr-cikis-onayla/', views.qr_cikis_onayla, name='qr_cikis_onayla'),
    path('qr-tarayici/', views.qr_tarayici, name='qr_tarayici'),
    path('katilimci-listesi/', views.katilimci_listesi, name='katilimci_listesi'),
    path('katilimci-ekle/', views.katilimci_ekle, name='katilimci_ekle'),
    path('katilimci-sil/<int:ticket_id>/', views.katilimci_sil, name='katilimci_sil'),
    path('katilimci-katildi/<int:ticket_id>/', views.katilimci_katildi, name='katilimci_katildi'),
    path('csv-indir/', views.csv_indir, name='csv_indir'),
    path('katilimcilari-sifirla/', views.katilimcilari_sifirla, name='katilimcilari_sifirla'),
    path('tum-katilimcilari-sil/', views.tum_katilimcilari_sil, name='tum_katilimcilari_sil'),
]