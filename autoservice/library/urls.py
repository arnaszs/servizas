from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('myorders/', views.UserOrdersListView.as_view(), name='my_orders'),
    path('mycars/', views.UserCarListView.as_view(), name='my_cars'),
    path('myorders/<int:pk>', views.UserOrderDetailView.as_view(), name='my_order'),
    path('myorders/new', views.UserOrderCreateView.as_view(), name='my-order-new')
]
