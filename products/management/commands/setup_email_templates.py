from django.core.management.base import BaseCommand
from products.models import EmailTemplate


class Command(BaseCommand):
    help = 'Setup default email templates'

    def handle(self, *args, **options):
        email_templates = [
            {
                'email_type': 'welcome',
                'subject': '👋 Welcome to RedCart!',
                'body': 'Welcome email body',
            },
            {
                'email_type': 'order_confirmation',
                'subject': '✅ Order Confirmed!',
                'body': 'Order confirmation email body',
            },
            {
                'email_type': 'order_shipped',
                'subject': '📦 Your Order Has Shipped',
                'body': 'Order shipped email body',
            },
            {
                'email_type': 'order_delivered',
                'subject': '🎉 Your Order Has Arrived!',
                'body': 'Order delivered email body',
            },
            {
                'email_type': 'password_reset',
                'subject': '🔐 Reset Your Password',
                'body': 'Password reset email body',
            },
            {
                'email_type': 'newsletter',
                'subject': '📬 Latest Updates from RedCart',
                'body': 'Newsletter email body',
            },
            {
                'email_type': 'contact_reply',
                'subject': '📧 We\'ve Received Your Message',
                'body': 'Contact reply email body',
            },
        ]

        for template in email_templates:
            obj, created = EmailTemplate.objects.get_or_create(
                email_type=template['email_type'],
                defaults={
                    'subject': template['subject'],
                    'body': template['body'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created email template: {template["email_type"]}')
                )
            else:
                # Ensure it's active
                if not obj.is_active:
                    obj.is_active = True
                    obj.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Activated email template: {template["email_type"]}')
                    )
                else:
                    self.stdout.write(f'⏭️  Email template already exists: {template["email_type"]}')

        self.stdout.write(self.style.SUCCESS('\n✅ All email templates are now active!'))
