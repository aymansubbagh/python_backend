from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='ayman@devai.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_succesful(self):
        """Test creating a new user with email is succesful"""
        email = 'ayman@dev.ai'
        password = 'aim12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'ayman@DEV.ai'
        user = get_user_model().objects.create_user(email, 'aim12345')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'aim12345')

    def test_create_new_super_user(self):
        """Creating super user"""
        user = get_user_model().objects.create_superuser(
            'ayman@dev.ai',
            'aim12345'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test that the recipe string representation is returned"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mashroom sauce',
            time_minute=5,
            price=5.00,
        )

        self.assertEqual(str(recipe), recipe.title)
