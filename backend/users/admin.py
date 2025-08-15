from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserAddress

class UserAddressInline(admin.TabularInline):
    model = UserAddress
    extra = 1
    fields = ['address_type', 'is_default', 'recipient_name', 'phone_number', 'address_line_1', 'city', 'state', 'country', 'zip_code']

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'full_name', 'phone_number', 'is_active', 
        'is_verified', 'has_complete_profile', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_verified', 
        'email_verified', 'phone_verified', 'date_joined', 'gender'
    ]
    search_fields = ['username', 'email', 'full_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'country', 'zip_code')
        }),
        ('Preferences', {
            'fields': ('is_newsletter_subscribed', 'marketing_emails', 'sms_notifications')
        }),
        ('Account Status', {
            'fields': ('is_verified', 'email_verified', 'phone_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Social Login', {
            'fields': ('facebook_id', 'google_id'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']
    inlines = [UserAddressInline]
    
    def has_complete_profile(self, obj):
        return obj.has_complete_profile
    has_complete_profile.boolean = True
    has_complete_profile.short_description = 'Complete Profile'
    
    actions = ['verify_users', 'unverify_users', 'activate_users', 'deactivate_users']
    
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
    verify_users.short_description = "Mark selected users as verified"
    
    def unverify_users(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_users.short_description = "Mark selected users as unverified"
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Deactivate selected users"

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'address_type', 'recipient_name', 'city', 'state', 
        'is_default', 'created_at'
    ]
    list_filter = ['address_type', 'is_default', 'city', 'state', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'recipient_name', 'city', 'state']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'address_type', 'is_default')
        }),
        ('Recipient Details', {
            'fields': ('recipient_name', 'phone_number')
        }),
        ('Address Details', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'zip_code')
        }),
        ('Additional Information', {
            'fields': ('landmark', 'delivery_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
