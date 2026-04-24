"""
Utility functions for RedCart e-commerce
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import EmailLog, EmailTemplate
import logging

logger = logging.getLogger(__name__)


# ============ EMAIL UTILITIES ============

def send_email(user, email_type, context=None, recipient_email=None):
    """
    Send email using templates
    
    Args:
        user: User object
        email_type: Type of email (e.g., 'order_confirmation')
        context: Dictionary with template context
        recipient_email: Override recipient email (default: user.email)
    """
    if context is None:
        context = {}
    
    try:
        # Get email template
        template = EmailTemplate.objects.filter(email_type=email_type, is_active=True).first()
        if not template:
            logger.warning(f"Email template not found: {email_type}")
            return False
        
        recipient = recipient_email or user.email
        
        # Add user to context
        context['user'] = user
        context['site_name'] = 'RedCart'
        
        # Render HTML template
        html_message = render_to_string(f'emails/{email_type}.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=template.subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Log email
        EmailLog.objects.create(
            user=user,
            email_type=email_type,
            recipient=recipient,
            subject=template.subject,
            status='sent'
        )
        
        logger.info(f"Email sent: {email_type} to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email {email_type}: {str(e)}")
        
        # Log failed email
        EmailLog.objects.create(
            user=user,
            email_type=email_type,
            recipient=recipient_email or user.email,
            subject='',
            status='failed'
        )
        return False


def send_order_confirmation_email(order):
    """Send order confirmation email"""
    context = {
        'order': order,
        'items': order.items.all(),
        'total': order.total,
    }
    return send_email(order.user, 'order_confirmation', context)


def send_order_shipped_email(order):
    """Send order shipped notification"""
    context = {
        'order': order,
        'tracking_number': order.tracking_number,
    }
    return send_email(order.user, 'order_shipped', context)


def send_order_delivered_email(order):
    """Send order delivered notification"""
    context = {'order': order}
    return send_email(order.user, 'order_delivered', context)


def send_welcome_email(user):
    """Send welcome email to new user"""
    context = {'username': user.username}
    return send_email(user, 'welcome', context)


def send_contact_reply_email(contact_submission, reply_message):
    """Send reply to contact form"""
    context = {
        'name': contact_submission.name,
        'subject': contact_submission.subject,
        'reply': reply_message,
    }
    return send_email(
        user=None,  # Contact forms might not have user account
        email_type='contact_reply',
        context=context,
        recipient_email=contact_submission.email
    )


# ============ INVENTORY UTILITIES ============

def update_stock(product, quantity, reason='adjustment'):
    """
    Update product stock with tracking
    
    Args:
        product: Product instance
        quantity: Amount to change (positive or negative)
        reason: Reason for change ('sale', 'return', 'restock', 'adjustment')
    """
    from .models import InventoryLog
    
    product.stock += quantity
    product.save()
    
    # Log the change
    InventoryLog.objects.create(
        product=product,
        quantity_changed=quantity,
        reason=reason
    )
    
    logger.info(f"Stock updated for {product.name}: {quantity} ({reason})")
    
    # Check if stock is low
    if product.stock < 5:
        logger.warning(f"Low stock alert for {product.name}: {product.stock} remaining")
    
    return product


def check_stock_availability(product, quantity, variant=None):
    """Check if sufficient stock is available"""
    if variant:
        return variant.stock >= quantity
    return product.stock >= quantity


# ============ ORDER UTILITIES ============

def generate_tracking_number(order_id):
    """Generate a tracking number for an order"""
    import uuid
    return f"RC-{order_id}-{str(uuid.uuid4())[:8].upper()}"


def calculate_tax(subtotal, tax_rate=0.075):
    """Calculate tax on order (7.5% for Nigeria)"""
    return round(subtotal * tax_rate, 2)


def apply_discount_code(code, subtotal):
    """
    Apply discount code and return discount amount
    
    Returns:
        (discount_amount, error_message) tuple
    """
    from .models import DiscountCode
    
    try:
        discount = DiscountCode.objects.get(code__iexact=code)
        
        if not discount.is_valid:
            return 0, "This discount code is no longer valid"
        
        if subtotal < discount.min_purchase:
            return 0, f"Minimum purchase of ₦{discount.min_purchase:,.2f} required"
        
        if discount.discount_type == 'percentage':
            discount_amount = subtotal * (discount.discount_value / 100)
        else:  # fixed
            discount_amount = discount.discount_value
        
        discount_amount = min(discount_amount, subtotal)  # Can't exceed subtotal
        
        return discount_amount, None
        
    except DiscountCode.DoesNotExist:
        return 0, "Invalid discount code"


# ============ RECOMMENDATION UTILITIES ============

def get_product_recommendations(product, limit=4):
    """Get recommended products for a given product"""
    from .models import ProductRecommendation
    
    try:
        recommendation = ProductRecommendation.objects.get(product=product)
        return recommendation.frequently_bought_with.all()[:limit]
    except ProductRecommendation.DoesNotExist:
        # If no recommendations exist, return related category products
        return product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:limit]


# ============ ANALYTICS UTILITIES ============

def track_product_view(product, user=None):
    """Track product views for analytics"""
    from .models import ProductView
    ProductView.objects.create(product=product, user=user)


def get_trending_products(days=30, limit=10):
    """Get trending products based on views"""
    from .models import ProductView
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    
    recent_date = timezone.now() - timedelta(days=days)
    
    return ProductView.objects.filter(
        viewed_at__gte=recent_date
    ).values('product').annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:limit]


# ============ PAGINATION UTILITIES ============

def paginate_queryset(queryset, page, items_per_page=None):
    """
    Paginate a queryset
    
    Returns:
        (paginated_items, total_pages, current_page) tuple
    """
    if items_per_page is None:
        items_per_page = settings.ITEMS_PER_PAGE
    
    total_items = queryset.count()
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    start = (page - 1) * items_per_page
    end = start + items_per_page
    
    paginated = queryset[start:end]
    
    return paginated, total_pages, page
