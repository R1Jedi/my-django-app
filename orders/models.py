from django.conf import settings
from django.core.mail import send_mail
from django.db import models

from products.models import Basket
from users.models import User


class Order(models.Model):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    STATUSES = (
        (CREATED, 'Создан'),
        (PAID, 'Оплачен'),
        (ON_WAY, 'В пути'),
        (DELIVERED, 'Доставлен')
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=256)
    address = models.CharField(max_length=256)
    basket_history = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=CREATED, choices=STATUSES)
    initiator = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order #{self.id}. {self.first_name} {self.last_name}"

    def update_after_payment(self):
        baskets = Basket.objects.filter(user=self.initiator)
        self.status = self.PAID
        self.basket_history = {
            'purchased_items': [basket.de_json() for basket in baskets],
            'total_sum': float(baskets.total_sum()),
        }
        baskets.delete()
        self.save()

        self.send_order_email()

    def send_order_email(self):
        """Отправляет email о заказе"""
        subject = f'Заказ #{self.id} успешно оплачен'
        message = f"""
            Уважаемый(ая) {self.first_name} {self.last_name}!

            Ваш заказ #{self.id} успешно оплачен.
            Статус: {self.get_status_display()}
            Адрес доставки: {self.address}
            Сумма заказа: {self.basket_history.get('total_sum', 0)} руб.

            Спасибо за покупку!
            """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email]
        )

    def send_status_update_email(self):
        """Отправляет email при изменении статуса"""
        if self.status == self.DELIVERED:
            subject = f'Ваш заказ #{self.id} доставлен'
            message = f"""
                Уважаемый(ая) {self.first_name} {self.last_name}!

                Ваш заказ #{self.id} был успешно доставлен по адресу: {self.address}

                Спасибо, что выбрали нас!
                """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
                fail_silently=False,
            )
