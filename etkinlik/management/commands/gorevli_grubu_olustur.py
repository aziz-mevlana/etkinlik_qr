from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Görevli grubunu oluşturur'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Görevli')
        if created:
            self.stdout.write(self.style.SUCCESS('Görevli grubu oluşturuldu.'))
        else:
            self.stdout.write(self.style.WARNING('Görevli grubu zaten mevcut.'))
