import uuid
from django.db import models

class Ticket(models.Model):
    CHOICES = (
        (1, "Bilişim Sistemleri Ve Teknolojileri"),
        (2, "Bankacılık Ve Sigortacılık"),
        (3, "Halkla İlişkiler Ve Reklamcılık"),
        (4, "Gümrük İşletme"),
        (5, "Uluslararası Ticaret Ve Finansman"),
        (6, "Diğer"),
    )
    name = models.CharField(max_length=100, null=True)
    student_id = models.CharField(max_length=10)
    department = models.IntegerField(choices=CHOICES, default=6)  # Varsayılan değer olarak "Diğer" (6) kullanılıyor
    qr_code = models.CharField(max_length=255, unique=True, blank=True)  # Her bilet için benzersiz QR kod verisi
    is_joined = models.BooleanField(default=False)  # Katılım onaylanıp onaylanmadığını belirtir
    entry_date = models.DateTimeField(null=True)  # İlk giriş tarihi
    leave_date = models.DateTimeField(null=True)  # Son giriş tarihi

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.student_id} - {self.department}"

class CheckIn(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    check_date = models.DateTimeField(auto_now_add=True)  # QR kodunun okutulduğu tarih ve saat

    def __str__(self):
        return f"{self.ticket.name} - {self.check_date}"