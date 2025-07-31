from .models import Product

def cart_count(request):
    """Add cart count to all templates"""
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    return {'cart_count': cart_count} 