from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the user api (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
                'email': 'test@dev.com',
                'password': 'testpasd',
                'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@dev.com',
            'password': 'testpasd',
            'name': 'Test name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 charicters"""
        payload = {
            'email': 'tdddddest1@dwwewsdev.com',
            'password': 'fg',
            'name': 'hassani',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token has been created for the user"""
        payload = {
            'email': 'yu@we.ioc.com',
            'password': 'rt56yt_',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        payload_r = {
            'email': 'yu@we.ioc.com',
            'password': 'rt56yt_',
        }
        create_user(**payload_r)

        payload_w = {
            'email': 'yu@we.ioc.com',
            'password': 'rt56345g',
        }
        res = self.client.post(TOKEN_URL, payload_w)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_a_user(self):
        """Test that token is not created if user does not exist"""
        payload = {
            'email': 'yu@we.ioc.com',
            'password': 'rt56345g',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_missing_fields(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {
            'email': 'yu@we.ioc.com',
            'password': 'rt56345g',
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unathorized(self):
        """Test that authentication is required for users"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTest(TestCase):
    """Test API requests that required for users"""

    def setUp(self):
        self.user = create_user(
            email='aymansubbagh@outlook.com',
            name='ayman subbagh',
            password='aim_89-21-73',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retriving profile for logged in users"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the ME URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""

        payload = {
            'name': 'aim',
            'password': 'SaUiBmGh_89-21@37'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
