from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.utils.html import format_html
from .models import (
    Product, Offer, Comment, Wishlist, Compare, Order, OrderItem,
    InventoryLog, ProductVariant, UserAddress, PaymentMethod,
    ShippingMethod, EmailTemplate, EmailLog, SupportTicket, TicketReply,
    FAQ, ProductView, ProductRecommendation, ContactFormSubmission,
    DiscountCode, Newsletter
)

# 🎨 Customize Admin Site
admin.site.site_header = "RedCart Admin Dashboard"
admin.site.site_title = "RedCart Admin"
admin.site.index_title = "Welcome to RedCart Admin"


# ============ PRODUCT MANAGEMENT ============

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'stock', 'sku', 'price_adjustment')


class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'price', 'stock', 'category', 'stock_status', 'flash_sale_status')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline]
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'description', 'price', 'category')}),
        ('Images', {'fields': ('image_url', 'image_2', 'image_3')}),
        ('Inventory', {'fields': ('stock',)}),
        ('Flash Sale', {'fields': ('sale_price', 'sale_ends_at'), 'classes': ('collapse',), 'description': 'Set a flash sale price and end time for this product. Leave empty to disable flash sale.'}),
    )
    
    def stock_status(self, obj):
        if obj.stock > 20:
            color = 'green'
            status = 'In Stock'
        elif obj.stock > 0:
            color = 'orange'
            status = 'Low Stock'
        else:
            color = 'red'
            status = 'Out of Stock'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    stock_status.short_description = 'Stock Status'

    def flash_sale_status(self, obj):
        if obj.has_active_sale:
            return format_html(
                '<span style="color: green; font-weight: bold;">⚡ Active Sale</span>'
            )
        elif obj.sale_price and obj.sale_ends_at:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏰ Sale Ended</span>'
            )
        else:
            return format_html(
                '<span style="color: gray;">No Sale</span>'
            )
    flash_sale_status.short_description = 'Flash Sale Status'


class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_changed', 'reason', 'created_at')
    list_filter = ('reason', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('product__name',)


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock', 'sku', 'final_price')
    list_filter = ('product', 'size', 'color')
    search_fields = ('sku', 'product__name')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('name', 'text', 'product__name')


# ============ ORDER MANAGEMENT ============

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price')
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status_badge', 'payment_status', 'escrow_status_badge', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'escrow_status', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'total')
    search_fields = ('user__username', 'user__email', 'tracking_number')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('user', 'status', 'payment_status')}),
        ('Shipping', {'fields': ('shipping_address', 'tracking_number', 'shipping_cost')}),
        ('Dates', {'fields': ('shipped_date', 'delivered_date')}),
        ('Payment', {'fields': ('payment_method', 'subtotal', 'tax', 'discount', 'insurance_opted', 'insurance_cost', 'is_paid')}),
        ('Escrow', {'fields': ('escrow_status', 'escrow_release_date', 'escrow_notes')}),
        ('Notes', {'fields': ('notes',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def order_id(self, obj):
        return format_html('<strong>Order #{}</strong>', obj.id)
    order_id.short_description = 'Order'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'confirmed': 'blue',
            'processing': 'orange',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
            'refunded': 'brown',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def escrow_status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'held': 'blue',
            'released': 'green',
            'disputed': 'red',
        }
        color = colors.get(obj.escrow_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_escrow_status_display()
        )
    escrow_status_badge.short_description = 'Escrow'


class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_type', 'base_cost', 'estimated_days', 'is_active')
    list_filter = ('shipping_type', 'is_active')


# ============ USER MANAGEMENT ============

class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'country', 'is_default')
    list_filter = ('country', 'is_default')
    search_fields = ('user__username', 'full_name', 'city')


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_type', 'is_default', 'is_active')
    list_filter = ('payment_type', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')


# ============ EMAIL & COMMUNICATION ============

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('email_type', 'is_active')
    list_filter = ('is_active',)


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_type', 'status', 'sent_at')
    list_filter = ('email_type', 'status', 'sent_at')
    readonly_fields = ('sent_at',)
    search_fields = ('user__username', 'recipient')


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    fields = ('admin', 'message', 'is_admin_reply', 'created_at')
    readonly_fields = ('created_at',)


class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'user', 'title', 'priority_badge', 'status_badge', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    search_fields = ('user__username', 'title', 'description')
    inlines = [TicketReplyInline]
    
    def ticket_id(self, obj):
        return format_html('<strong>Ticket #{}</strong>', obj.id)
    ticket_id.short_description = 'Ticket'
    
    def priority_badge(self, obj):
        colors = {'low': 'green', 'medium': 'yellow', 'high': 'orange', 'urgent': 'red'}
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {'open': 'blue', 'in_progress': 'orange', 'resolved': 'green', 'closed': 'gray'}
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# ============ MARKETING & CONTENT ============

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    ordering = ('order',)


class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('created_at', 'name', 'email', 'subject', 'message')
    search_fields = ('name', 'email', 'subject')


class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'validity_status', 'current_usage')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until')
    readonly_fields = ('current_usage',)
    search_fields = ('code',)
    
    def validity_status(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green; font-weight: bold;">✓ Valid</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Invalid</span>')
    validity_status.short_description = 'Status'


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed', 'created_at')
    list_filter = ('subscribed', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('email',)


class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ('product',)
    search_fields = ('product__name',)


class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'viewed_at')
    list_filter = ('product', 'viewed_at')
    readonly_fields = ('viewed_at',)
    search_fields = ('product__name', 'user__username')


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__name')


class CompareAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__name')


class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'discount')


# ============ REGISTER ALL MODELS ============

# Products
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(InventoryLog, InventoryLogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Offer, OfferAdmin)

# Orders
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingMethod, ShippingMethodAdmin)

# User Management
admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)

# Email & Communication
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(EmailLog, EmailLogAdmin)
admin.site.register(SupportTicket, SupportTicketAdmin)

# Content & Marketing
admin.site.register(FAQ, FAQAdmin)
admin.site.register(ContactFormSubmission, ContactFormSubmissionAdmin)
admin.site.register(DiscountCode, DiscountCodeAdmin)
admin.site.register(Newsletter, NewsletterAdmin)

# Analytics
admin.site.register(ProductView, ProductViewAdmin)
admin.site.register(ProductRecommendation, ProductRecommendationAdmin)

# Wishlist & Compare
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Compare, CompareAdmin)