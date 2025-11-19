from django.contrib import admin
from django.urls import path
from app.shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #Главная страница
    path('', views.HomePageView.as_view(), name='home'),

    # Item
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('buy/<int:pk>/', views.BuyItemView.as_view(), name='buy_item'),
    
    # Order
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('buy_order/<int:pk>/', views.BuyOrderView.as_view(), name='buy_order'),
    
    # Success и Cancelled
    path('success/', views.SuccessView.as_view(), name='success'),
    path('cancelled/', views.CancelView.as_view(), name='cancelled'),
]
