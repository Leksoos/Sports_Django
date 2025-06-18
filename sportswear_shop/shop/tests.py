from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from shop.models import Product, Category, Brand
from reviews.models import Review

User = get_user_model()

class ShopTests(TestCase):
    def setUp(self) -> None:
        """
        Подготавливает тестовую среду: создаёт пользователя, товар и т.д.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.category = Category.objects.create(name='Обувь')
        self.brand = Brand.objects.create(name='Nike')
        self.product = Product.objects.create(
            name='Кроссовки', price=1000, category=self.category, brand=self.brand
        )

    def test_product_creation(self) -> None:
        """
        Проверяет создание товара.
        """
        self.assertEqual(Product.objects.count(), 1)

    def test_review_creation(self):
        review = Review.objects.create(product=self.product, user=self.user, rating=5, comment='Отлично!')
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)

    def test_review_unique_constraint(self):
        Review.objects.create(product=self.product, user=self.user, rating=5, comment='Отлично!')
        with self.assertRaises(IntegrityError):
            Review.objects.create(product=self.product, user=self.user, rating=4, comment='Хорошо')

    def test_review_form_valid(self):
        from reviews.forms import ReviewForm
        form = ReviewForm({'rating': 5, 'comment': 'Тест'})
        self.assertTrue(form.is_valid())

    def test_review_form_invalid(self):
        from reviews.forms import ReviewForm
        form = ReviewForm({'rating': 5, 'comment': ''})
        self.assertFalse(form.is_valid())

    def test_product_list_view(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        url = reverse('product_detail', args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_review_not_authenticated(self):
        url = reverse('add_review', args=[self.product.pk])
        response = self.client.post(url, {'rating': 5, 'comment': 'Тест'})

    def test_add_review_authenticated(self):
        self.client.login(username='testuser', password='pass')
        url = reverse('add_review', args=[self.product.pk])
        response = self.client.post(url, {'rating': 5, 'comment': 'Тест'})
        self.assertEqual(Review.objects.count(), 1)

    def test_delete_review(self):
        self.client.login(username='testuser', password='pass')
        review = Review.objects.create(product=self.product, user=self.user, rating=5, comment='Тест')
        url = reverse('delete_review', args=[review.pk])
        response = self.client.post(url)
        self.assertEqual(Review.objects.count(), 0)