from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Brand, Product, ProductImage, ProductVariant
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories = [
            {'name': 'Men\'s Clothing', 'description': 'Fashionable clothing for men'},
            {'name': 'Women\'s Clothing', 'description': 'Elegant clothing for women'},
            {'name': 'Kids Clothing', 'description': 'Comfortable clothing for children'},
            {'name': 'Accessories', 'description': 'Fashion accessories and jewelry'},
            {'name': 'Footwear', 'description': 'Shoes, sandals, and boots'},
        ]
        
        created_categories = []
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create brands
        brands = [
            {'name': 'Fashion Forward', 'description': 'Trendy and modern fashion'},
            {'name': 'Classic Style', 'description': 'Timeless and elegant designs'},
            {'name': 'Urban Trend', 'description': 'Street style and casual wear'},
            {'name': 'Luxury Brand', 'description': 'Premium quality fashion items'},
        ]
        
        created_brands = []
        for brand_data in brands:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            created_brands.append(brand)
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        # Create products
        products_data = [
            {
                'name': 'Men\'s Casual T-Shirt',
                'description': 'Comfortable cotton t-shirt for everyday wear',
                'category': created_categories[0],
                'brand': created_brands[0],
                'price': Decimal('25.99'),
                'sale_price': Decimal('19.99'),
                'stock': 100,
                'is_featured': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Women\'s Summer Dress',
                'description': 'Beautiful summer dress perfect for any occasion',
                'category': created_categories[1],
                'brand': created_brands[1],
                'price': Decimal('45.99'),
                'sale_price': None,
                'stock': 50,
                'is_featured': True,
                'is_new_arrival': False,
            },
            {
                'name': 'Kids Comfortable Jeans',
                'description': 'Durable and comfortable jeans for active children',
                'category': created_categories[2],
                'brand': created_brands[2],
                'price': Decimal('35.99'),
                'sale_price': Decimal('29.99'),
                'stock': 75,
                'is_featured': False,
                'is_new_arrival': True,
            },
            {
                'name': 'Stylish Sunglasses',
                'description': 'Trendy sunglasses with UV protection',
                'category': created_categories[3],
                'brand': created_brands[3],
                'price': Decimal('89.99'),
                'sale_price': Decimal('69.99'),
                'stock': 30,
                'is_featured': True,
                'is_new_arrival': False,
            },
            {
                'name': 'Comfortable Sneakers',
                'description': 'Lightweight sneakers perfect for daily use',
                'category': created_categories[4],
                'brand': created_brands[0],
                'price': Decimal('79.99'),
                'sale_price': None,
                'stock': 60,
                'is_featured': False,
                'is_new_arrival': True,
            },
        ]
        
        created_products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            created_products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create product variants
        for product in created_products:
            if 'T-Shirt' in product.name or 'Dress' in product.name:
                sizes = ['S', 'M', 'L', 'XL']
                colors = ['Red', 'Blue', 'Black', 'White']
                
                for size in sizes:
                    for color in colors:
                        ProductVariant.objects.get_or_create(
                            product=product,
                            name='Size',
                            value=size,
                            defaults={'stock': random.randint(10, 30)}
                        )
                        ProductVariant.objects.get_or_create(
                            product=product,
                            name='Color',
                            value=color,
                            defaults={'stock': random.randint(10, 30)}
                        )
            elif 'Jeans' in product.name:
                sizes = ['2T', '3T', '4T', '5T', '6T']
                colors = ['Blue', 'Black']
                
                for size in sizes:
                    for color in colors:
                        ProductVariant.objects.get_or_create(
                            product=product,
                            name='Size',
                            value=size,
                            defaults={'stock': random.randint(15, 25)}
                        )
                        ProductVariant.objects.get_or_create(
                            product=product,
                            name='Color',
                            value=color,
                            defaults={'stock': random.randint(15, 25)}
                        )
            elif 'Sneakers' in product.name:
                sizes = ['7', '8', '9', '10', '11']
                colors = ['White', 'Black', 'Gray']
                
                for size in sizes:
                    for color in colors:
                        ProductVariant.objects.get_or_create(
                            product=product,
                            name='Size',
                            value=size,
                            defaults={'stock': random.randint(8, 20)}
                        )
                        ProductVariant.objects.get_or_create(
                            product=product,
                            name='Color',
                            value=color,
                            defaults={'stock': random.randint(8, 20)}
                        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write(f'Created {len(created_categories)} categories')
        self.stdout.write(f'Created {len(created_brands)} brands')
        self.stdout.write(f'Created {len(created_products)} products')
        self.stdout.write(f'Created {ProductVariant.objects.count()} product variants')