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
    student_id = models.CharField(max_length=10, unique=True)
    department = models.IntegerField(choices=CHOICES, default=6)
    qr_code = models.CharField(max_length=255, unique=True, blank=True)

    OTURUMLAR = [
        (1, "Gün 1 - Oturum 1"),
        (2, "Gün 1 - Oturum 2"),
        (3, "Gün 2 - Oturum 1"),
        (4, "Gün 2 - Oturum 2"),
        (5, "Gün 3 - Oturum 1"),
        (6, "Gün 3 - Oturum 2"),
    ]

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = f"ID:{self.student_id}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def katildigi_oturumlar(self):
        return list(self.yoklama_set.values_list('oturum', flat=True))

    def toplam_katilim(self):
        return self.yoklama_set.count()

    def __str__(self):
        return f"{self.name} - {self.student_id}"


class Yoklama(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    oturum = models.IntegerField()
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ticket', 'oturum')

    def __str__(self):
        return f"{self.ticket.name} - Oturum {self.oturum}"


class AktifOturum(models.Model):
    oturum = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        AktifOturum.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_aktif(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'oturum': 1})
        return obj.oturum

    def __str__(self):
        return f"Aktif Oturum: {self.oturum}"
