import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404
from .models import Item, Order

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomePageView(TemplateView):
    """
    Главная страница.
    Отображает список всех доступных товаров и созданных заказов.
    """
    template_name = 'shop/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.all()
        context['orders'] = Order.objects.all()
        return context

class ItemDetailView(TemplateView):
    """
    Страница просмотра отдельного товара.
    Передает публичный ключ Stripe в контекст шаблона.
    """
    template_name = 'shop/item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = get_object_or_404(Item, pk=self.kwargs['pk'])
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context

class BuyItemView(View):
    """
    API Endpoint для покупки одного товара.
    Создает сессию Stripe Checkout для конкретного Item.
    Возвращает JSON с session_id.
    """
    def get(self, request, pk, *args, **kwargs):
        item = get_object_or_404(Item, pk=pk)
        domain_url = 'http://localhost:8000/' # В проде использовать request.build_absolute_uri('/')
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': item.currency,
                    'unit_amount': item.price,
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=domain_url + 'success/',
            cancel_url=domain_url + 'cancelled/',
        )
        return JsonResponse({'id': checkout_session.id})

class OrderDetailView(TemplateView):
    """
    Страница просмотра заказа.
    Показывает состав заказа, примененные налоги и скидки.
    """
    template_name = 'shop/order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        context['order'] = order
        context['items'] = order.items.all()
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context

class BuyOrderView(View):
    """
    API Endpoint для оплаты целого заказа (Order).
    Динамически создает Stripe Coupon и Stripe TaxRate, если они указаны в заказе.
    Формирует сессию с списком всех товаров.
    """
    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        domain_url = 'http://localhost:8000/'

        # 1. Создание купона в Stripe (если есть скидка)
        stripe_coupon_id = None
        if order.discount:
            try:
                coupon = stripe.Coupon.create(
                    percent_off=order.discount.percent_off,
                    duration='once',
                    name=order.discount.name
                )
                stripe_coupon_id = coupon.id
            except Exception as e:
                print(f"Error creating coupon: {e}")

        # 2. Создание налоговой ставки в Stripe (если есть налог)
        stripe_tax_rate_id = None
        if order.tax:
            try:
                tax_rate = stripe.TaxRate.create(
                    display_name=order.tax.name,
                    inclusive=False,
                    percentage=float(order.tax.rate),
                )
                stripe_tax_rate_id = tax_rate.id
            except Exception as e:
                print(f"Error creating tax rate: {e}")

        # 3. Формирование списка товаров
        line_items = []
        for item in order.items.all():
            item_data = {
                'price_data': {
                    'currency': item.currency,
                    'unit_amount': item.price,
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                },
                'quantity': 1,
            }
            
            if stripe_tax_rate_id:
                item_data['tax_rates'] = [stripe_tax_rate_id]
            
            line_items.append(item_data)

        # 4. Создание сессии
        session_data = {
            'payment_method_types': ['card'],
            'line_items': line_items,
            'mode': 'payment',
            'success_url': domain_url + 'success/',
            'cancel_url': domain_url + 'cancelled/',
        }

        if stripe_coupon_id:
            session_data['discounts'] = [{'coupon': stripe_coupon_id}]

        checkout_session = stripe.checkout.Session.create(**session_data)
        return JsonResponse({'id': checkout_session.id})

class SuccessView(TemplateView):
    """Страница успешной оплаты."""
    template_name = 'shop/success.html'

class CancelView(TemplateView):
    """Страница отмены оплаты."""
    template_name = 'shop/cancelled.html'