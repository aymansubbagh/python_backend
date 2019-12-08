from django.test import TestCase
from django.contrib.auth import get_user_model


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
