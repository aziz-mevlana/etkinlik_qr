# Admin giriş
lisa
1234

# Etkinlik Katılım Sistemi

Bu proje, etkinlik katılımcılarını yönetmek için bir Django tabanlı web uygulamasıdır. Kullanıcılar etkinliklere katılım sağlayabilir, QR kodları oluşturabilir ve katılımcı listelerini yönetebilirler.

## Kurulum

### Gereksinimler

- Python 3.x
- Django==5.1.7
- asgiref==3.8.1
- certifi==2025.1.31
- charset-normalizer==3.4.1
- colorama==0.4.6
- idna==3.10
- pillow==11.1.0
- qrcode==8.0
- requests==2.32.3
- sqlparse==0.5.3
- tzdata==2025.1
- urllib3==2.3.0

### Adımlar

1. Bu projeyi klonlayın:
    ```bash
    git clone https://github.com/aziz-mevlana/etkinlik_qr.git
    cd etkinlik_qr
    ```

2. Sanal bir ortam oluşturun ve etkinleştirin:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows için: venv\Scripts\activate
    ```

3. Gerekli paketleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

4. Veritabanını oluşturun ve gerekli migrasyonları uygulayın:
    ```bash
    python manage.py migrate
    ```

5. Geliştirme sunucusunu başlatın:
    ```bash
    python manage.py runserver
    ```

6. Tarayıcınızda `http://127.0.0.1:8000/` adresine gidin.

## Kullanım

### Katılımcı Ekleme

1. Ana sayfada katılım formunu doldurun ve "Katılım Oluştur" butonuna tıklayın.
2. QR kodunuz oluşturulacak ve ekranda görüntülenecektir.

### Katılımcı Listesi

1. `http://127.0.0.1:8000/katilimci-listesi/` adresine gidin.
2. Katılım yapan ve yapmayan katılımcıları görüntüleyin.
3. Yeni katılımcı eklemek için formu doldurun ve "Ekle" butonuna tıklayın.

### Katılımcı Silme

1. Katılımcı listesinde, silmek istediğiniz katılımcının yanındaki çöp kutusu ikonuna tıklayın.

### Katılım Onaylama

1. Katılım yapmayanlar listesinde, katılımı onaylamak istediğiniz katılımcının yanındaki onay ikonuna tıklayın.

## Proje Yapısı

- `etkinlik/`: Django uygulaması için ana dizin.
- `etkinlik/templates/etkinlik/`: HTML şablon dosyaları.
- `etkinlik/static/etkinlik/`: Statik dosyalar (CSS, JS).
- `etkinlik/views.py`: Görünümler.
- `etkinlik/forms.py`: Formlar.
- `etkinlik/models.py`: Veritabanı modelleri.
- `etkinlik/urls.py`: URL yönlendirmeleri.

## Katkıda Bulunma

Katkıda bulunmak isterseniz, lütfen bir pull request gönderin veya bir issue açın.
