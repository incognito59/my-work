"""
Utility functions for RedCart e-commerce
"""
import json
import re
import requests

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
        template = EmailTemplate.objects.filter(email_type=email_type, is_active=True).first()
        if not template:
            logger.warning(f"Email template not found: {email_type}")
            return False

        recipient = recipient_email or user.email

        context['user'] = user
        context['site_name'] = 'RedCart'

        html_message = render_to_string(f'emails/{email_type}.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=template.subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )

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
    """Send reply to contact form submission"""
    context = {
        'name': contact_submission.name,
        'subject': contact_submission.subject,
        'reply': reply_message,
    }
    return send_email(
        user=None,
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

    InventoryLog.objects.create(
        product=product,
        quantity_changed=quantity,
        reason=reason
    )

    logger.info(f"Stock updated for {product.name}: {quantity} ({reason})")

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
        else:
            discount_amount = discount.discount_value

        discount_amount = min(discount_amount, subtotal)

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
        return Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:limit]


# ============ AI UTILITIES (Groq) ============

def _call_groq(prompt, max_tokens=250):
    """Send a prompt to Groq and return the assistant response."""
    api_key = getattr(settings, 'GROQ_API_KEY', '')

    if not api_key:
        raise RuntimeError('Groq API key is not configured.')

    payload = {
        'model': 'llama-3.1-8b-instant',
        'max_tokens': max_tokens,
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'Mozilla/5.0',
    }

    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            json=payload,
            headers=headers,
            timeout=20
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.HTTPError as exc:
        logger.error('Groq API error (%s): %s', exc.response.status_code, exc.response.text)
        return ''
    except (KeyError, IndexError) as exc:
        logger.error('Unexpected Groq API response structure: %s', exc)
        return ''
    except Exception as exc:
        logger.error('Groq API request failed: %s', exc)
        return ''


def _parse_ai_items(text, limit=4):
    """Parse a plain-text AI response into a list of product names."""
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


def get_product_recommendations_ai(product, limit=4):
    """Ask Groq AI for smart product recommendations using catalog data."""
    try:
        candidates = list(Product.objects.filter(category=product.category).exclude(id=product.id)[:20])
        if not candidates:
            return get_product_recommendations(product, limit)

        candidate_lines = [
            f"{c.name} — ₦{c.price:,.2f} — {c.description[:80].strip()}"
            for c in candidates
        ]

        prompt = (
            f"You are a helpful shopping assistant for RedCart. The customer is viewing:\n"
            f"Name: {product.name}\n"
            f"Category: {product.category}\n"
            f"Price: ₦{product.price:,.2f}\n"
            f"Description: {product.description.strip()}\n\n"
            f"From the catalog below, recommend up to {limit} products the customer is most likely to like. "
            f"Return only the exact product names, one per line.\n\n"
            f"Catalog:\n" + '\n'.join(candidate_lines)
        )

        response_text = _call_groq(prompt, max_tokens=220)
        selected_names = _parse_ai_items(response_text, limit=limit)

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
        logger.error('Error fetching AI recommendations: %s', exc)

    return get_product_recommendations(product, limit)


def get_ai_chat_response(message, limit=4):
    """Build an AI chat response using product catalog context."""
    try:
        products = list(Product.objects.all().order_by('-id')[:25])
        product_lines = [
            f"{p.name} — Category: {p.category} — ₦{p.price:,.2f} — {p.description[:80].strip()}"
            for p in products
        ]

        prompt = (
            f"You are the RedCart AI shopping assistant. Use only the product details below to answer customer questions. "
            f"Recommend only actual items from the catalog. Do not invent products.\n\n"
            f"Catalog:\n" + '\n'.join(product_lines) + "\n\n"
            f"User question: {message}\n\n"
            f"Answer clearly, mention product names and prices when relevant. "
            f"If nothing matches, say so and suggest available alternatives."
        )

        response_text = _call_groq(prompt, max_tokens=320)
        if response_text:
            return response_text
    except RuntimeError:
        pass
    except Exception as exc:
        logger.error('AI chat failed: %s', exc)

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