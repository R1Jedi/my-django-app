from http import HTTPStatus
from unittest.mock import patch, MagicMock
import stripe

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from orders.models import Order
from products.models import Product, ProductCategory, Basket

User = get_user_model()


class OrderCreateViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mail.ru',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('orders:order_create')

    def test_order_create_get(self):
        """Тест GET запроса на страницу оформления заказа"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], "Store - Оформление Заказа")
        self.assertTemplateUsed(response, 'orders/order-create.html')
        self.assertIsNotNone(response.context_data['form'])

    @patch('orders.views.stripe.checkout.Session.create')
    def test_order_create_post_success(self, mock_stripe_session):
        """Тест успешного оформления заказа"""
        # Используем товар из фикстур
        product = Product.objects.get(pk=1)
        Basket.objects.create(user=self.user, product=product, quantity=2)

        # Мокаем Stripe ответ
        mock_session = MagicMock()
        mock_session.url = 'https://stripe.com/checkout'
        mock_stripe_session.return_value = mock_session

        order_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': 'Test Address 123'
        }

        response = self.client.post(self.url, order_data)

        # Проверяем редирект на Stripe
        self.assertEqual(response.status_code, HTTPStatus.SEE_OTHER)
        self.assertEqual(response.url, 'https://stripe.com/checkout')

        # Проверяем создание заказа
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.last_name, 'Doe')
        self.assertEqual(order.initiator, self.user)
        self.assertEqual(order.status, Order.CREATED)

        # Проверяем вызов Stripe API
        mock_stripe_session.assert_called_once()

    @patch('orders.views.stripe.checkout.Session.create')
    def test_order_create_post_empty_basket(self, mock_stripe_session):
        """Тест оформления заказа с пустой корзиной"""
        order_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': 'Test Address 123'
        }

        response = self.client.post(self.url, order_data)

        # При пустой корзине заказ должен создаваться, но Stripe не должен вызываться
        order = Order.objects.first()
        self.assertIsNotNone(order)

        # Должен быть редирект на страницу успеха
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('orders:order_success'))

        # Stripe не должен вызываться при пустой корзине
        mock_stripe_session.assert_not_called()


class SuccessTemplateViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('orders:order_success')

    def test_success_page(self):
        """Тест страницы успешного заказа"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], "Store - Спасибо за заказ!")
        self.assertTemplateUsed(response, 'orders/success.html')


class CanceledTemplateViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('orders:order_canceled')

    def test_canceled_page(self):
        """Тест страницы отмененного заказа"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'orders/canceled.html')


class OrderListViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mail.ru',
            password='testpassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@mail.ru',
            password='otherpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('orders:orders_list')

        # Создаем заказы для разных пользователей
        self.order1 = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='Address 1',
            initiator=self.user
        )
        self.order2 = Order.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            address='Address 2',
            initiator=self.user
        )
        self.other_order = Order.objects.create(
            first_name='Other',
            last_name='User',
            email='other@example.com',
            address='Address 3',
            initiator=self.other_user
        )

    def test_order_list_authenticated(self):
        """Тест списка заказов для авторизованного пользователя"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], "Store - Заказы")
        self.assertTemplateUsed(response, 'orders/orders.html')

        # Проверяем что видны только заказы текущего пользователя
        orders = response.context_data['object_list']
        self.assertEqual(orders.count(), 2)
        self.assertIn(self.order1, orders)
        self.assertIn(self.order2, orders)
        self.assertNotIn(self.other_order, orders)

    def test_order_list_ordering(self):
        """Тест порядка отображения заказов (новые first)"""
        response = self.client.get(self.url)
        orders = list(response.context_data['object_list'])

        # Проверяем что заказы отсортированы по убыванию даты создания
        self.assertEqual(orders[0].id, self.order2.id)  # Последний созданный
        self.assertEqual(orders[1].id, self.order1.id)  # Первый созданный

    def test_order_list_unauthenticated(self):
        """Тест списка заказов для неавторизованного пользователя"""
        self.client.logout()
        response = self.client.get(self.url)

        # Должен быть редирект на страницу логина
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsNotNone(response.url)


class OrderDetailViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mail.ru',
            password='testpassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@mail.ru',
            password='otherpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='Test Address',
            initiator=self.user
        )
        self.url = reverse('orders:order', kwargs={'pk': self.order.pk})

    def test_order_detail_own_order(self):
        """Тест просмотра своего заказа"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'orders/order.html')
        self.assertEqual(response.context_data['title'], f"Store - Заказ #{self.order.id}")
        self.assertEqual(response.context_data['object'], self.order)

    def test_order_detail_other_user_order(self):
        """Тест попытки просмотра чужого заказа"""
        other_order = Order.objects.create(
            first_name='Other',
            last_name='User',
            email='other@example.com',
            address='Other Address',
            initiator=self.other_user
        )
        url = reverse('orders:order', kwargs={'pk': other_order.pk})

        response = self.client.get(url)

        # Должен вернуть 403 (Forbidden) или 404
        self.assertIn(response.status_code, [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND])


class StripeWebhookTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mail.ru',
            password='testpassword'
        )

    @patch('orders.views.stripe.Webhook.construct_event')
    @patch('orders.views.fulfill_order')
    def test_stripe_webhook_success(self, mock_fulfill, mock_construct):
        """Тест успешного Stripe webhook"""
        # Создаем заказ для теста
        order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='Test Address',
            initiator=self.user,
            status=Order.CREATED
        )

        # Мокаем событие Stripe
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'test_session_id',
                    'metadata': {'order_id': str(order.id)}
                }
            }
        }
        mock_construct.return_value = mock_event

        response = self.client.post(
            '/webhook/stripe/',
            data='{"test": "data"}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_fulfill.assert_called_once()

    @patch('orders.views.stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct):
        """Тест webhook с невалидной подписью"""
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "sig_header"
        )

        response = self.client.post(
            '/webhook/stripe/',
            data='{"test": "data"}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )

        self.assertEqual(response.status_code, 400)

    def test_stripe_webhook_invalid_payload(self):
        """Тест webhook с невалидными данными"""
        response = self.client.post(
            '/webhook/stripe/',
            data='invalid json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, 400)


class FulfillOrderTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mail.ru',
            password='testpassword'
        )

    def test_fulfill_order(self):
        """Тест обработки оплаченного заказа"""
        # Создаем заказ и товары в корзине
        order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='Test Address',
            initiator=self.user,
            status=Order.CREATED
        )

        # Используем товар из фикстур
        product = Product.objects.get(pk=1)
        basket = Basket.objects.create(user=self.user, product=product, quantity=2)

        # Создаем мок сессии Stripe (как словарь)
        mock_session = {
            'metadata': {'order_id': str(order.id)}
        }

        # Вызываем функцию
        from orders.views import fulfill_order
        fulfill_order(mock_session)

        # Обновляем данные из БД
        order.refresh_from_db()

        # Проверяем что заказ оплачен и корзина очищена
        self.assertEqual(order.status, Order.PAID)
        self.assertIsNotNone(order.basket_history)
        self.assertFalse(Basket.objects.filter(user=self.user).exists())