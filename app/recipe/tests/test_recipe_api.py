from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os
from PIL import Image

RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return url for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recpie(user=self.user)

        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        url = detail_url(recipe.id)
        payload = {'title': 'Chicken', 'tags': [new_tag.id]}

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        tags = recipe.tags.all()

        self.assertEqual(recipe.title, payload['title'])
        self.assertIn(new_tag, tags)
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags.count(), 1)

    def test_full_update_recipe(self):
        """ Test updating a recipe with put"""
        recipe = sample_recpie(user=self.user)

        recipe.tags.add(sample_tag(user=self.user))
        new_tag_1 = sample_tag(user=self.user, name='chips')
        new_tag_2 = sample_tag(user=self.user, name='nachos')

        payload = {
            'title': 'potato',
            'time_minute': 23,
            'price': 45.00,
            'tags': [new_tag_1.id, new_tag_2.id]
        }
        url = detail_url(recipe.id)

        self.client.put(url, payload)

        tags = recipe.tags.all()

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minute, payload['time_minute'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertIn(new_tag_1, tags)
        self.assertIn(new_tag_2, tags)
        self.assertEqual(tags.count(), 2)


class RecipeImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'aidev@aidev.org'
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recpie(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.JPEG') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipe_by_tags(self):
        """Test returning recipe with a specific tags"""
        recipe_1 = sample_recpie(user=self.user, title="Thai Vegtable Curry")
        recipe_2 = sample_recpie(user=self.user, title="Aubergine with tahini")

        tag_1 = sample_tag(user=self.user, name='Vegan')
        tag_2 = sample_tag(user=self.user, name='Vegetarian')

        recipe_1.tags.add(tag_1)
        recipe_2.tags.add(tag_2)

        recipe_3 = sample_recpie(user=self.user, title='Fish and chips')

        res = self.client.get(
            RECIPE_URL,
            {'tags': f'{tag_1.id},{tag_2.id}'}
        )

        serializer_1 = RecipeSerializer(recipe_1)
        serializer_2 = RecipeSerializer(recipe_2)
        serializer_3 = RecipeSerializer(recipe_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)

    def test_filter_recipe_by_ingredients(self):
        """Test returning recipe with a specific ingredients"""
        recipe_1 = sample_recpie(user=self.user, title="White Rice")
        recipe_2 = sample_recpie(user=self.user, title="Brown Rice")

        ingredient_1 = sample_ingredient(user=self.user, name='Salt')
        ingredient_2 = sample_ingredient(user=self.user, name='Rice')

        recipe_1.ingredients.add(ingredient_1)
        recipe_2.ingredients.add(ingredient_2)

        recipe_3 = sample_recpie(user=self.user, title='Fish and chips')

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient_1.id},{ingredient_2.id}'}
        )

        serializer_1 = RecipeSerializer(recipe_1)
        serializer_2 = RecipeSerializer(recipe_2)
        serializer_3 = RecipeSerializer(recipe_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)
