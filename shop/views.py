from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Wishlist


def home(request):
    """Home page view"""
    # Get featured products (first 8 products)
    featured_products = Product.objects.all()[:8]
    
    # Get user's wishlist items for highlighting
    wishlist_items = []
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_items = wishlist.products.all()
    
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'wishlist_items': wishlist_items,
    })

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    # Get user's wishlist items for highlighting
    wishlist_items = []
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_items = wishlist.products.all()
    
    return render(request, 'shop/product_list.html', {
        'products': products,
        'wishlist_items': wishlist_items,
        'query': query
    })

def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })
            total += product.price * quantity
        except Product.DoesNotExist:
            pass
    
    return render(request, 'shop/cart.html', {
        'cart_items': products,
        'total': total
    })

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            cart[str(product_id)] += 1
        else:
            cart[str(product_id)] = 1
        
        request.session['cart'] = cart
        messages.success(request, f'{product.name} added to cart!')
        
    return redirect('product_list')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart!')
    
    return redirect('cart_view')

def clear_cart(request):
    request.session['cart'] = {}
    messages.success(request, 'Cart has been cleared!')
    return redirect('cart_view')

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if product not in wishlist.products.all():
            wishlist.products.add(product)
            messages.success(request, f'{product.name} added to wishlist!')
        else:
            messages.info(request, f'{product.name} is already in your wishlist!')
    
    return redirect('product_list')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.success(request, f'{product.name} removed from wishlist!')
    
    return redirect('wishlist_view')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('product_list')
    
    products = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })
            total += product.price * quantity
        except Product.DoesNotExist:
            pass
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        if name and email and address:
            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                address=address,
                cart_data=cart,
                total_price=total
            )
            
            # Clear cart
            request.session['cart'] = {}
            messages.success(request, 'Order placed successfully!')
            return redirect('thank_you', order_id=order.id)
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'shop/checkout.html', {
        'cart_items': products,
        'total': total
    })

def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/thank_you.html', {'order': order})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    previous_url = request.META.get('HTTP_REFERER', '/')
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'previous_url': previous_url
    })
