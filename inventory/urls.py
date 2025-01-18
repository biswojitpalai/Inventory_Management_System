from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', Index.as_view(),name='index'),
    path('signup/',SignUpView.as_view(),name='signup'),
    path('add-item',AddItem.as_view(),name='add-item'),
    path('edit-item/<int:pk>',EditItem.as_view(),name='edit-item'),
    path('delete-item/<int:pk>',DeleteItem.as_view(),name='delete-item'),
    path('update-quantity/<int:pk>/', UpdateQuantityView.as_view(), name='update-quantity'),
    path('dashboard/',Dashboard.as_view(),name='dashboard'),
    path('export-inventory/', ExportInventoryView.as_view(), name='export-inventory'),
    path('login/',auth_views.LoginView.as_view(template_name='inventory/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='inventory/logout.html', http_method_names = ['get', 'post', 'options']),name='logout'),
    path('clear-all-entries/', clear_all_entries, name='clear-all-entries'),
    path('add-to-cart/<int:item_id>/', add_to_cart, name='add-to-cart'),
    path('cart/', view_cart, name='cart'),
    path('update-cart/<int:item_id>/', update_cart, name='update-cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove-from-cart'),
    path('clear-cart/', clear_cart, name='clear-cart'),
    path('checkout/', checkout, name='checkout'),
    path("payment/", payment, name="payment"),
    path("confirm_payment/", confirm_payment, name="confirm_payment"),
]
