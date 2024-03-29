from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='locator'),
    path('cost_estimates/', views.cost_estimates, name='cost_estimates'),
    path('customer_form/', views.customer_form, name='customer_form'),
    path('complete_view/', views.complete_view, name='complete_view'),
    path('quotation/<int:id>/', views.export_quote, name='export_quote'),
    path('orders/', views.orders_view, name='orders_view'),
    path('order/<int:pk>/', views.single_order, name='single_order'),
    path('admin/order/<order_id>/', views.admin_order_pdf, name='admin_order_pdf'),
]
