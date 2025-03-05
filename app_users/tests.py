from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

UserModel = get_user_model()


class RegisterApiTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('users:register')  # Update with the actual URL name
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }

    def test_successful_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "Confirmation code has been sent to your email")
        self.assertTrue(UserModel.objects.filter(email=self.user_data["email"]).exists())

    def test_password_mismatch(self):
        self.user_data["password2"] = "WrongPass123!"
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Passwords do not match")

    def test_missing_fields(self):
        invalid_data = {
            "username": "johndoe",
            "email": "johndoe@example.com"
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('password2', response.data)
