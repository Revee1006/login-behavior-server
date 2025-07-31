from django.urls import path
from .views import order_history, signup_view, login_view, logout_view

urlpatterns = [
    path('orders/', order_history, name='order_history'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
] 