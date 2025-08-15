import hashlib
import requests
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Order

class SSLCommerzPayment:
    """
    SSL Commerz Payment Gateway Integration
    """
    
    def __init__(self):
        self.store_id = settings.SSL_COMMERZ_STORE_ID
        self.store_password = settings.SSL_COMMERZ_STORE_PASSWORD
        self.sandbox = settings.SSL_COMMERZ_SANDBOX
        
        if self.sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
        else:
            self.base_url = "https://securepay.sslcommerz.com"
    
    def create_session(self, order, customer_ip, success_url=None, fail_url=None, cancel_url=None):
        """
        Create SSL Commerz payment session
        """
        if not success_url:
            success_url = f"{settings.SITE_URL}{reverse('payment_success')}"
        if not fail_url:
            fail_url = f"{settings.SITE_URL}{reverse('payment_fail')}"
        if not cancel_url:
            cancel_url = f"{settings.SITE_URL}{reverse('payment_cancel')}"
        
        # Prepare payment data
        payment_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'total_amount': float(order.total_amount),
            'currency': 'BDT',
            'tran_id': order.order_number,
            'product_category': 'Fashion',
            'product_name': f"Order {order.order_number}",
            'cus_name': order.customer_name,
            'cus_email': order.customer_email,
            'cus_add1': order.shipping_address,
            'cus_city': order.shipping_city,
            'cus_state': order.shipping_state,
            'cus_postcode': order.shipping_zip_code,
            'cus_country': order.shipping_country,
            'cus_phone': order.customer_phone,
            'cus_fax': '',
            'ship_name': order.customer_name,
            'ship_add1': order.shipping_address,
            'ship_city': order.shipping_city,
            'ship_state': order.shipping_state,
            'ship_postcode': order.shipping_zip_code,
            'ship_country': order.shipping_country,
            'shipping_method': 'NO',
            'product_profile': 'general',
            'num_of_item': order.items.count(),
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'ipn_url': f"{settings.SITE_URL}{reverse('payment_ipn')}",
            'multi_card_name': '',
            'value_a': str(order.id),
            'value_b': order.customer_email,
            'value_c': order.customer_phone,
            'value_d': str(order.user.id),
        }
        
        # Add product details
        for i, item in enumerate(order.items.all()):
            payment_data[f'product_name_{i+1}'] = item.product_name
            payment_data[f'product_category_{i+1}'] = 'Fashion'
            payment_data[f'product_profile_{i+1}'] = 'general'
            payment_data[f'amount_{i+1}'] = float(item.unit_price)
            payment_data[f'quantity_{i+1}'] = item.quantity
        
        # Generate hash
        hash_string = f"{self.store_id}{order.order_number}{float(order.total_amount)}BDT{order.customer_email}{self.store_password}"
        payment_data['signature'] = hashlib.md5(hash_string.encode()).hexdigest()
        
        # Make API call to create session
        try:
            response = requests.post(
                f"{self.base_url}/gwprocess/v4/api.php",
                data=payment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'SUCCESS':
                    # Update order with session key
                    order.ssl_sessionkey = result.get('sessionkey')
                    order.save()
                    
                    return {
                        'status': 'success',
                        'session_key': result.get('sessionkey'),
                        'gateway_url': result.get('GatewayPageURL'),
                        'redirect_url': result.get('redirectGatewayURL')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': result.get('failedreason', 'Payment session creation failed')
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP Error: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Network Error: {str(e)}'
            }
    
    def validate_payment(self, session_key, transaction_id):
        """
        Validate payment after successful transaction
        """
        validation_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'sessionkey': session_key,
            'tran_id': transaction_id,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/validator/api/validationserverAPI.php",
                data=validation_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'VALID':
                    return {
                        'status': 'success',
                        'data': result
                    }
                else:
                    return {
                        'status': 'error',
                        'message': result.get('errorMessage', 'Payment validation failed')
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP Error: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Network Error: {str(e)}'
            }
    
    def refund_payment(self, transaction_id, amount, refund_reason):
        """
        Process refund for a transaction
        """
        refund_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'tran_id': transaction_id,
            'refund_amount': amount,
            'refund_remarks': refund_reason,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/validator/api/refund.php",
                data=refund_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'SUCCESS':
                    return {
                        'status': 'success',
                        'refund_id': result.get('refund_id'),
                        'message': 'Refund processed successfully'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': result.get('errorMessage', 'Refund failed')
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP Error: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Network Error: {str(e)}'
            }

class PaymentProcessor:
    """
    Main payment processor class
    """
    
    def __init__(self):
        self.ssl_commerz = SSLCommerzPayment()
    
    def process_payment(self, order, customer_ip, success_url=None, fail_url=None, cancel_url=None):
        """
        Process payment for an order
        """
        # Validate order
        if not order or order.payment_status == 'paid':
            return {
                'status': 'error',
                'message': 'Invalid order or already paid'
            }
        
        # Create payment session
        session_result = self.ssl_commerz.create_session(
            order, customer_ip, success_url, fail_url, cancel_url
        )
        
        if session_result['status'] == 'success':
            return session_result
        else:
            return session_result
    
    def complete_payment(self, session_key, transaction_id):
        """
        Complete payment after successful transaction
        """
        # Validate payment
        validation_result = self.ssl_commerz.validate_payment(session_key, transaction_id)
        
        if validation_result['status'] == 'success':
            # Find order by session key
            try:
                order = Order.objects.get(ssl_sessionkey=session_key)
                
                # Update order status
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.transaction_id = transaction_id
                order.ssl_tran_id = transaction_id
                order.save()
                
                # Update product stock
                for item in order.items.all():
                    product = item.product
                    if item.variant:
                        variant = item.variant
                        variant.stock = max(0, variant.stock - item.quantity)
                        variant.save()
                    else:
                        product.stock = max(0, product.stock - item.quantity)
                        product.save()
                
                return {
                    'status': 'success',
                    'order': order,
                    'message': 'Payment completed successfully'
                }
                
            except Order.DoesNotExist:
                return {
                    'status': 'error',
                    'message': 'Order not found'
                }
        else:
            return validation_result
    
    def process_refund(self, transaction_id, amount, refund_reason):
        """
        Process refund for a transaction
        """
        return self.ssl_commerz.refund_payment(transaction_id, amount, refund_reason)