from django.core.management.base import BaseCommand
from products.models import Offer


class Command(BaseCommand):
    help = 'Create sample offers for testing'

    def handle(self, *args, **options):
        sample_offers = [
            {
                'code': 'SAVE10',
                'description': 'Save 10% on all products with code SAVE10',
                'discount': 10.0
            },
            {
                'code': 'WELCOME20',
                'description': 'Welcome offer: 20% off for new customers',
                'discount': 20.0
            },
            {
                'code': 'FLASH15',
                'description': 'Flash sale: 15% off on selected items',
                'discount': 15.0
            },
            {
                'code': 'SUMMER25',
                'description': 'Summer special: Up to 25% off on summer collection',
                'discount': 25.0
            },
        ]

        for offer_data in sample_offers:
            offer, created = Offer.objects.get_or_create(
                code=offer_data['code'],
                defaults={
                    'description': offer_data['description'],
                    'discount': offer_data['discount']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created offer: {offer.code} - {offer.description}')
                )
            else:
                self.stdout.write(f'⏭️  Offer already exists: {offer.code}')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample offers created/verified!'))
