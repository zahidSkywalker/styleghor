from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import json

from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    Cart, CartItem, Order, OrderItem, Review, Wishlist,
    Coupon, NewsletterSubscription
)
from .payment import PaymentProcessor

User = get_user_model()

def home(request):
    """Home page with featured products and categories"""
    featured_products = Product.objects.filter(
        is_featured=True, 
        status='active',
        stock__gt=0
    )[:8]
    
    bestseller_products = Product.objects.filter(
        is_bestseller=True, 
        status='active',
        stock__gt=0
    )[:8]
    
    new_arrivals = Product.objects.filter(
        is_new_arrival=True, 
        status='active',
        stock__gt=0
    )[:8]
    
    categories = Category.objects.filter(is_active=True)[:6]
    
    context = {
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)

def product_list(request):
    """Product listing page with filters"""
    products = Product.objects.filter(status='active', stock__gt=0)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Brand filter
    brand_slug = request.GET.get('brand', '')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(current_price__gte=min_price)
    if max_price:
        products = products.filter(current_price__lte=max_price)
    
    # Sort
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('current_price')
    elif sort_by == 'price_high':
        products = products.order_by('-current_price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'popularity':
        products = products.annotate(review_count=Count('reviews')).order_by('-review_count')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filters for sidebar
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'search_query': search_query,
        'category_slug': category_slug,
        'brand_slug': brand_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, status='active')
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        status='active',
        stock__gt=0
    ).exclude(id=product.id)[:4]
    
    # Get reviews
    reviews = Review.objects.filter(product=product, is_approved=True)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
    }
    return render(request, 'shop/product_detail.html', context)

@login_required
def add_to_cart(request):
    """Add product to cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            variant_id = data.get('variant_id')
            quantity = int(data.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id, status='active')
            
            # Check stock
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
                if variant.stock < quantity:
                    return JsonResponse({'status': 'error', 'message': 'Insufficient stock'})
            else:
                if product.stock < quantity:
                    return JsonResponse({'status': 'error', 'message': 'Insufficient stock'})
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True,
                defaults={'is_active': True}
            )
            
            # Check if item already exists
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant_id=variant_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Product added to cart',
                'cart_count': cart.total_items
            })
            
        except (json.JSONDecodeError, ValueError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Invalid data'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def cart_view(request):
    """Cart view page"""
    try:
        cart = Cart.objects.get(user=request.user, is_active=True)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart.html', context)

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            
            if quantity <= 0:
                cart_item.delete()
                return JsonResponse({'status': 'success', 'message': 'Item removed from cart'})
            
            # Check stock
            if cart_item.variant:
                if cart_item.variant.stock < quantity:
                    return JsonResponse({'status': 'error', 'message': 'Insufficient stock'})
            else:
                if cart_item.product.stock < quantity:
                    return JsonResponse({'status': 'error', 'message': 'Insufficient stock'})
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cart updated',
                'item_total': float(cart_item.total_price),
                'cart_total': float(cart_item.cart.total_price)
            })
            
        except (json.JSONDecodeError, ValueError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Invalid data'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    messages.success(request, 'Item removed from cart')
    return redirect('cart')

@login_required
def checkout(request):
    """Checkout page"""
    try:
        cart = Cart.objects.get(user=request.user, is_active=True)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    # Get user addresses
    user_addresses = request.user.addresses.all()
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = 60.00  # Fixed shipping cost for now
    tax_amount = subtotal * 0.05  # 5% tax
    total_amount = subtotal + shipping_cost + tax_amount
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'user_addresses': user_addresses,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
@require_POST
def place_order(request):
    """Place order"""
    try:
        cart = Cart.objects.get(user=request.user, is_active=True)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    # Get form data
    shipping_address_id = request.POST.get('shipping_address')
    billing_address_id = request.POST.get('billing_address')
    payment_method = request.POST.get('payment_method')
    notes = request.POST.get('notes', '')
    
    # Get addresses
    try:
        shipping_address = request.user.addresses.get(id=shipping_address_id)
        billing_address = request.user.addresses.get(id=billing_address_id) if billing_address_id else shipping_address
    except:
        messages.error(request, 'Please select valid addresses')
        return redirect('checkout')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = 60.00
    tax_amount = subtotal * 0.05
    total_amount = subtotal + shipping_cost + tax_amount
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        customer_name=request.user.display_name,
        customer_email=request.user.email,
        customer_phone=request.user.phone_number or '',
        shipping_address=shipping_address.address_line_1,
        shipping_city=shipping_address.city,
        shipping_state=shipping_address.state,
        shipping_country=shipping_address.country,
        shipping_zip_code=shipping_address.zip_code,
        billing_address=billing_address.address_line_1,
        billing_city=billing_address.city,
        billing_state=billing_address.state,
        billing_country=billing_address.country,
        billing_zip_code=billing_address.zip_code,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        total_amount=total_amount,
        payment_method=payment_method,
        notes=notes,
    )
    
    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            variant=cart_item.variant,
            product_name=cart_item.product.name,
            product_sku=cart_item.product.sku,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.current_price,
            total_price=cart_item.total_price,
        )
    
    # Clear cart
    cart.is_active = False
    cart.save()
    
    # Redirect to payment
    if payment_method == 'ssl_commerz':
        return redirect('process_payment', order_id=order.id)
    else:
        # For cash on delivery
        order.payment_status = 'pending'
        order.status = 'confirmed'
        order.save()
        messages.success(request, 'Order placed successfully!')
        return redirect('order_confirmation', order_id=order.id)

@login_required
def process_payment(request, order_id):
    """Process payment with SSL Commerz"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        messages.info(request, 'Order is already paid')
        return redirect('order_confirmation', order_id=order.id)
    
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    
    # Process payment
    payment_processor = PaymentProcessor()
    payment_result = payment_processor.process_payment(order, client_ip)
    
    if payment_result['status'] == 'success':
        # Redirect to SSL Commerz
        return redirect(payment_result['redirect_url'])
    else:
        messages.error(request, f'Payment error: {payment_result["message"]}')
        return redirect('checkout')

@login_required
def payment_success(request):
    """Payment success callback"""
    session_key = request.GET.get('sessionkey')
    transaction_id = request.GET.get('tran_id')
    
    if not session_key or not transaction_id:
        messages.error(request, 'Invalid payment response')
        return redirect('home')
    
    # Complete payment
    payment_processor = PaymentProcessor()
    result = payment_processor.complete_payment(session_key, transaction_id)
    
    if result['status'] == 'success':
        messages.success(request, 'Payment successful! Your order has been confirmed.')
        return redirect('order_confirmation', order_id=result['order'].id)
    else:
        messages.error(request, f'Payment verification failed: {result["message"]}')
        return redirect('home')

@login_required
def payment_fail(request):
    """Payment failure callback"""
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('checkout')

@login_required
def payment_cancel(request):
    """Payment cancellation callback"""
    messages.warning(request, 'Payment was cancelled.')
    return redirect('checkout')

@csrf_exempt
def payment_ipn(request):
    """Payment IPN (Instant Payment Notification)"""
    if request.method == 'POST':
        # Process IPN data
        # This is for server-to-server communication
        pass
    return HttpResponse('OK')

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Send confirmation email
    try:
        subject = f'Order Confirmation - {order.order_number}'
        message = render_to_string('shop/emails/order_confirmation.html', {
            'order': order,
            'user': request.user
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])
    except Exception as e:
        print(f"Email sending failed: {e}")
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_confirmation.html', context)

@login_required
def order_history(request):
    """User order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)

@login_required
@require_POST
def add_review(request, product_id):
    """Add product review"""
    product = get_object_or_404(Product, id=product_id)
    
    rating = int(request.POST.get('rating', 5))
    title = request.POST.get('title', '')
    comment = request.POST.get('comment', '')
    
    if not comment:
        messages.error(request, 'Please provide a comment')
        return redirect('product_detail', slug=product.slug)
    
    # Check if user already reviewed
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        existing_review.rating = rating
        existing_review.title = title
        existing_review.comment = comment
        existing_review.is_approved = False  # Require re-approval
        existing_review.save()
        messages.success(request, 'Review updated successfully!')
    else:
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment,
        )
        messages.success(request, 'Review submitted successfully!')
    
    return redirect('product_detail', slug=product.slug)

@login_required
def wishlist(request):
    """User wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'shop/wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, 'Product added to wishlist')
    else:
        messages.info(request, 'Product is already in your wishlist')
    
    return redirect('product_detail', slug=product.slug)

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    
    messages.success(request, 'Product removed from wishlist')
    return redirect('wishlist')

def newsletter_subscribe(request):
    """Newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if email:
            subscription, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if created:
                messages.success(request, 'Successfully subscribed to newsletter!')
            else:
                if subscription.is_active:
                    messages.info(request, 'You are already subscribed to our newsletter!')
                else:
                    subscription.is_active = True
                    subscription.unsubscribed_at = None
                    subscription.save()
                    messages.success(request, 'Successfully re-subscribed to newsletter!')
        else:
            messages.error(request, 'Please provide a valid email address')
    
    return redirect('home')

def category_detail(request, slug):
    """Category detail page"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        status='active',
        stock__gt=0
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'shop/category_detail.html', context)

def brand_detail(request, slug):
    """Brand detail page"""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(
        brand=brand,
        status='active',
        stock__gt=0
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'page_obj': page_obj,
    }
    return render(request, 'shop/brand_detail.html', context)
