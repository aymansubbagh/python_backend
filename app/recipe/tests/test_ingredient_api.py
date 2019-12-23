from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTest(TestCase):
    """Test the publicly avaible ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to access the endpoint"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApitests(TestCase):
    """Test the private ingredient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'aim@devai.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retreive_ingredient_list(self):
        """Test retreiving of list ingredient"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test that ingredient for the autherized user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@devai.com',
            'passtest'
        )

        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Turmic')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
