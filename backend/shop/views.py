from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.http import JsonResponse

def product_list(request):
    products = Product.objects.all()
    data = [{"id": p.id, "name": p.name, "price": str(p.price), "image": p.image.url} for p in products]
    return JsonResponse(data, safe=False)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = {"id": product.id, "name": product.name, "price": str(product.price), "image": product.image.url, "description": product.description}
    return JsonResponse(data)
