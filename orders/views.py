from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from common.views import TitleMixin
from orders.forms import OrderForm
from orders.models import Order
from products.models import Basket


class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = 'orders/success.html'
    title = "Store - Спасибо за заказ!"


class CanceledTemplateView(TemplateView):
    template_name = 'orders/canceled.html'


class OrderCreateView(TitleMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:order_success')
    title = "Store - Оформление Заказа"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        order = form.save()

        baskets = Basket.objects.filter(user=self.request.user)
        if not baskets.exists():
            return redirect('products:index')

        order.basket_history = {
            'purchased_items': [basket.de_json() for basket in baskets],
            'total_sum': float(baskets.total_sum()),
        }
        order.save()

        baskets.delete()
        order.send_order_email()

        messages.success(self.request, 'Заказ успешно оформлен! Наш менеджер свяжется с вами.')
        return redirect(self.success_url)


class OrderListView(TitleMixin, LoginRequiredMixin, ListView):
    template_name = 'orders/orders.html'
    title = "Store - Заказы"
    queryset = Order.objects.all()
    ordering = '-created'

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order.html'
    model = Order

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.initiator != self.request.user:
            raise PermissionDenied("У вас нет доступа к этому заказу")
        return obj

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['title'] = f"Store - Заказ #{self.object.id}"
        return context
