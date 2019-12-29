from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='main'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnmon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recpie(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minute': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recpie API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateREcpieApiTest(TestCase):
    """Test unauthenticated recpie API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'auim@devai.com',
            'pass12334',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieve a List of recipes"""
        sample_recpie(user=self.user)
        sample_recpie(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recpie_limited_to_user(self):
        """Retrieving recipe list from user"""
        user2 = get_user_model().objects.create_user(
            'other@devai.com'
            'pass1223'
        )
        sample_recpie(user=user2)
        sample_recpie(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recpie(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'shakshu8a',
            'time_minute': 5,
            'price': 5.00,
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Meat')

        payload = {
            'title': 'eggs and sasuage',
            'time_minute': 5,
            'price': 5.00,
            'tags': [tag1.id, tag2.id],
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # my way of testing
        self.assertEqual(res.data['tags'], payload['tags'])

        # tutor's way of testing
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredent(self):
        """Test creating recipe with ingredent"""
        ingredients1 = sample_ingredient(user=self.user, name='butter')
        ingredients2 = sample_ingredient(user=self.user, name='popcorn')

        payload = {
            'title': 'buttered popcorn',
            'time_minute': 5,
            'price': 15.00,
            'ingredients': [ingredients1.id, ingredients2.id]
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # my way of testing
        self.assertEqual(res.data['ingredients'], payload['ingredients'])

        # tutor's way of testing
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredient = recipe.ingredients.all()
        self.assertEqual(ingredient.count(), 2)
        self.assertIn(ingredients1, ingredient)
        self.assertIn(ingredients2, ingredient)
