"""
Utility functions for RedCart e-commerce
"""
import json
import re
import urllib.request
import urllib.error

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import EmailLog, EmailTemplate, Product
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
        return Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:limit]


def _call_claude(prompt, max_tokens=250):
    """Send a prompt to Claude and return the assistant completion."""
    api_key = getattr(settings, 'CLAUDE_API_KEY', '')
    endpoint = getattr(settings, 'CLAUDE_API_URL', 'https://api.anthropic.com/v1/complete')

    if not api_key:
        raise RuntimeError('Claude API key is not configured.')

    payload = {
        'model': 'claude-sonnet-4-20250514',
        'prompt': f'Human: {prompt}\n\nAssistant:',
        'max_tokens_to_sample': max_tokens,
        'temperature': 0.3,
        'top_p': 1,
        'stop_sequences': ['\n\nHuman:'],
    }

    request_data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        endpoint,
        data=request_data,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode('utf-8'))
            return body.get('completion', '').strip()
    except urllib.error.HTTPError as exc:
        logger.error('Claude API error (%s): %s', exc.code, exc.read().decode('utf-8'))
        return ''
    except Exception as exc:
        logger.error('Claude API request failed: %s', exc)
        return ''


def _parse_claude_items(text, limit=4):
    """Parse a plain-text Claude response into a list of product names."""
    if not text:
        return []

    candidates = []
    for part in re.split(r'[\r\n;]+', text):
        line = part.strip()
        if not line:
            continue
        line = re.sub(r'^[\d\s\-\.\)]+', '', line).strip()
        if line:
            candidates.append(line)
        if len(candidates) >= limit:
            break
    return candidates


def get_claude_product_recommendations(product, limit=4):
    """Ask Claude for smart recommendations using catalog data."""
    try:
        candidates = list(Product.objects.filter(category=product.category).exclude(id=product.id)[:20])
        if not candidates:
            return get_product_recommendations(product, limit)

        candidate_lines = []
        for candidate in candidates:
            candidate_lines.append(
                f"{candidate.name} — ₦{candidate.price:,.2f} — {candidate.description[:80].strip()}"
            )

        prompt = (
            f"You are a helpful shopping assistant for RedCart. The customer is viewing the following product:\n"
            f"Name: {product.name}\n"
            f"Category: {product.category}\n"
            f"Price: ₦{product.price:,.2f}\n"
            f"Description: {product.description.strip()}\n\n"
            f"From this catalog of similar products, recommend up to {limit} products the customer is most likely to like. "
            f"Return only the exact product names from the list below, one per line.\n\n"
            f"Catalog:\n" + '\n'.join(candidate_lines)
        )

        response_text = _call_claude(prompt, max_tokens=220)
        selected_names = _parse_claude_items(response_text, limit=limit)

        recommendations = []
        for name in selected_names:
            matched = Product.objects.filter(name__iexact=name).first()
            if matched and matched.id != product.id:
                recommendations.append(matched)
            if len(recommendations) >= limit:
                break

        if recommendations:
            return recommendations

    except RuntimeError:
        pass
    except Exception as exc:
        logger.error('Error fetching Claude recommendations: %s', exc)

    return get_product_recommendations(product, limit)


def get_ai_chat_response(message, limit=4):
    """Build a Claude chat response using product catalog context."""
    try:
        products = list(Product.objects.all().order_by('-id')[:25])
        product_lines = []
        for product in products:
            product_lines.append(
                f"{product.name} — Category: {product.category} — ₦{product.price:,.2f} — {product.description[:80].strip()}"
            )

        prompt = (
            f"You are the RedCart AI shopping assistant. Use only the product details provided below to answer customer questions. "
            f"If the customer asks for products, recommend only actual available items from the catalog. Do not invent products.\n\n"
            f"Catalog:\n" + '\n'.join(product_lines) + "\n\n"
            f"User question: {message}\n\n"
            f"Answer clearly, mention product names and prices when relevant, and if nothing matches, say that no exact match exists while suggesting other available items."
        )

        response_text = _call_claude(prompt, max_tokens=320)
        if response_text:
            return response_text
    except RuntimeError:
        pass
    except Exception as exc:
        logger.error('AI chat failed: %s', exc)

    # Fallback response if Claude isn't configured or fails
    return (
        'Sorry, the AI assistant is unavailable right now. ' 
        'Browse our product categories or use the search bar to find items.'
    )


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
