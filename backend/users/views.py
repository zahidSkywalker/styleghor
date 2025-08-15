from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import json

from .models import CustomUser, UserAddress
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserAddressForm

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Auto-activate for now
            user.save()
            
            # Send welcome email
            try:
                subject = 'Welcome to Style Ghor!'
                message = render_to_string('users/emails/welcome.html', {
                    'user': user
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception as e:
                print(f"Welcome email failed: {e}")
            
            # Auto-login
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Style Ghor!')
            return redirect('shop:home')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Register'
    }
    return render(request, 'users/register.html', context)

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Update last login IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    client_ip = x_forwarded_for.split(',')[0]
                else:
                    client_ip = request.META.get('REMOTE_ADDR')
                user.last_login_ip = client_ip
                user.save()
                
                messages.success(request, f'Welcome back, {user.display_name}!')
                
                # Redirect to next page or home
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('shop:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'users/login.html', context)

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:home')

@login_required
def profile(request):
    """User profile page"""
    user = request.user
    
    # Get user statistics
    total_orders = user.orders.count()
    total_reviews = user.reviews.count()
    total_wishlist_items = user.wishlist.count()
    
    # Get recent orders
    recent_orders = user.orders.order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'total_orders': total_orders,
        'total_reviews': total_reviews,
        'total_wishlist_items': total_wishlist_items,
        'recent_orders': recent_orders,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=user)
    
    context = {
        'form': form,
        'title': 'Edit Profile'
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def change_password(request):
    """Change user password"""
    user = request.user
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('users:change_password')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('users:change_password')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('users:change_password')
        
        user.set_password(new_password1)
        user.save()
        
        # Re-login user
        login(request, user)
        messages.success(request, 'Password changed successfully!')
        return redirect('users:profile')
    
    context = {
        'title': 'Change Password'
    }
    return render(request, 'users/change_password.html', context)

@login_required
def address_list(request):
    """List user addresses"""
    addresses = request.user.addresses.all()
    
    context = {
        'addresses': addresses,
        'title': 'My Addresses'
    }
    return render(request, 'users/address_list.html', context)

@login_required
def add_address(request):
    """Add new address"""
    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is the first address, make it default
            if not request.user.addresses.exists():
                address.is_default = True
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('users:address_list')
    else:
        form = UserAddressForm()
    
    context = {
        'form': form,
        'title': 'Add New Address'
    }
    return render(request, 'users/add_address.html', context)

@login_required
def edit_address(request, address_id):
    """Edit existing address"""
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('users:address_list')
    else:
        form = UserAddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
        'title': 'Edit Address'
    }
    return render(request, 'users/edit_address.html', context)

@login_required
def delete_address(request, address_id):
    """Delete address"""
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('users:address_list')
    
    context = {
        'address': address,
        'title': 'Delete Address'
    }
    return render(request, 'users/delete_address.html', context)

@login_required
def set_default_address(request, address_id):
    """Set address as default"""
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    with transaction.atomic():
        # Remove default from all addresses
        request.user.addresses.update(is_default=False)
        # Set this address as default
        address.is_default = True
        address.save()
    
    messages.success(request, 'Default address updated successfully!')
    return redirect('users:address_list')

@login_required
def account_settings(request):
    """Account settings page"""
    user = request.user
    
    if request.method == 'POST':
        # Handle newsletter preferences
        newsletter_subscribed = request.POST.get('newsletter_subscribed') == 'on'
        marketing_emails = request.POST.get('marketing_emails') == 'on'
        sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        user.is_newsletter_subscribed = newsletter_subscribed
        user.marketing_emails = marketing_emails
        user.sms_notifications = sms_notifications
        user.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('users:account_settings')
    
    context = {
        'user': user,
        'title': 'Account Settings'
    }
    return render(request, 'users/account_settings.html', context)

@login_required
def delete_account(request):
    """Delete user account"""
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if not request.user.check_password(password):
            messages.error(request, 'Password is incorrect.')
            return redirect('users:delete_account')
        
        # Delete user (this will cascade to related objects)
        username = request.user.username
        request.user.delete()
        
        messages.success(request, f'Account {username} has been deleted successfully.')
        return redirect('shop:home')
    
    context = {
        'title': 'Delete Account'
    }
    return render(request, 'users/delete_account.html', context)

def forgot_password(request):
    """Forgot password functionality"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate password reset token (simplified for now)
            # In production, use proper password reset functionality
            
            # Send reset email
            try:
                subject = 'Password Reset Request - Style Ghor'
                message = render_to_string('users/emails/password_reset.html', {
                    'user': user
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                
                messages.success(request, 'Password reset instructions have been sent to your email.')
            except Exception as e:
                messages.error(request, 'Failed to send password reset email. Please try again.')
                print(f"Password reset email failed: {e}")
                
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    context = {
        'title': 'Forgot Password'
    }
    return render(request, 'users/forgot_password.html', context)

@login_required
def verify_email(request):
    """Email verification"""
    user = request.user
    
    if user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('users:profile')
    
    if request.method == 'POST':
        # Send verification email
        try:
            subject = 'Verify Your Email - Style Ghor'
            message = render_to_string('users/emails/email_verification.html', {
                'user': user
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            
            messages.success(request, 'Verification email sent successfully!')
        except Exception as e:
            messages.error(request, 'Failed to send verification email. Please try again.')
            print(f"Verification email failed: {e}")
    
    context = {
        'title': 'Verify Email'
    }
    return render(request, 'users/verify_email.html', context)

@login_required
def verify_phone(request):
    """Phone verification"""
    user = request.user
    
    if not user.phone_number:
        messages.error(request, 'Please add a phone number first.')
        return redirect('users:edit_profile')
    
    if user.phone_verified:
        messages.info(request, 'Your phone number is already verified.')
        return redirect('users:profile')
    
    if request.method == 'POST':
        # In production, implement SMS verification
        # For now, just mark as verified
        user.phone_verified = True
        user.save()
        messages.success(request, 'Phone number verified successfully!')
        return redirect('users:profile')
    
    context = {
        'title': 'Verify Phone'
    }
    return render(request, 'users/verify_phone.html', context)
