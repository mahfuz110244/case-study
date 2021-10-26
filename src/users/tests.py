import json

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
class UserBaseTestCase(APITestCase):
    def setUp(self):
        self.login_url = reverse("users:auth-login")
        self.employee_url = reverse("users:employee-list")
        self.restaurant_url = reverse("restaurant:restaurant-list")
        self.menu_url = reverse("restaurant:restaurant-menu-list")

        self.vote_url = reverse("vote:vote-list")
        self.vote_result_url = reverse("vote:voting-result-today")
        self.vote_result_publish_url = reverse("vote:voting-result-publish")
        # Create Employee and Manager Group
        self.employee_group = Group.objects.create(name=settings.EMPLOYEE)
        self.manager_group = Group.objects.create(name=settings.MANAGER)
        # create a super user
        self.admin_data = {
            'username': "admin",
            'first_name': "admin",
            'last_name': "main",
            'email': "admin@gmail.com",
            'password': "admin"
        }

        self.employee_data = {
            "employee_id": "employee1",
            "user": {
                "username": "employee1",
                "password": "bs23",
                "password2": "bs23",
                "email": "employee1@gmail.com",
                "first_name": "Employee",
                "last_name": "1"
            }
        }

        self.employee_data_two = {
            "employee_id": "employee2",
            "user": {
                "username": "employee2",
                "password": "bs23",
                "password2": "bs23",
                "email": "employee2@gmail.com",
                "first_name": "Employee",
                "last_name": "2"
            }
        }
        self.admin = User.objects.create_superuser(**self.admin_data)
        self.admin_access_token = self.get_jwt_token(self.admin_data)
        self.employee_creation(self.employee_data)
        self.employee_creation(self.employee_data_two)
        self.employee_access_token = self.get_jwt_token(self.employee_data['user'])
        self.employee_access_token_two = self.get_jwt_token(self.employee_data_two['user'])

        self.user_data = {
            'username': "mahfuz11",
            'first_name': "Mahfuzur Rahman",
            'last_name': "Khan",
            'email': "mahfuzku11@gmail.com",
            'password': "bs23"
        }

        self.user_register_data = {
            'username': "user1",
            'first_name': "User",
            'last_name': "One",
            'email': "user1@gmail.com",
            'password': "bs23",
            "password2": "bs23",
        }
        self.user = User.objects.create_user(**self.user_data)

        self.restaurant_data = {
            "name": "Restaurant Test 1",
            "address": "Dhaka, Dhanmondi",
            "latitude": 23.7470304,
            "longitude": 90.3671072,
            "phone": "+8801520103197",
            "manager": {
                "username": "manager1",
                "password": "bs23",
                "password2": "bs23",
                "email": "manager1@gmail.com",
                "first_name": "Manager",
                "last_name": "1"
            }
        }

        self.restaurant_data_two = {
            "name": "Restaurant Test 2",
            "address": "Dhaka, Dhanmondi",
            "latitude": 23.7470304,
            "longitude": 90.3671072,
            "phone": "+8801520103196",
            "manager": {
                "username": "manager2",
                "password": "bs23",
                "password2": "bs23",
                "email": "manager2@gmail.com",
                "first_name": "Manager",
                "last_name": "2"
            }
        }

    def get_jwt_token(self, user_data):
        url = self.login_url
        data = {"username": user_data['username'], "password": user_data['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token_data = json.loads(response.content)['data']
        self.assertTrue("access" in token_data.keys())
        access_token = token_data.get('access', "")
        return access_token

    def employee_creation(self, user_data):
        """
        Create a employee with user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        self.client.post(self.employee_url, user_data, format='json')


class UserAuthenticationTestCase(UserBaseTestCase):
    def test_user_registration_login(self):
        """
        Ensure we can register a new user, login and logout
        """
        url = reverse("users:auth-register")
        data = self.user_register_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse("users:auth-login")
        data = {"username": self.user_register_data['username'], "password": self.user_register_data['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token_data = json.loads(response.content)['data']
        self.assertTrue("refresh" in token_data.keys())
        self.assertTrue("access" in token_data.keys())
        access_token = token_data.get('access', "")
        refresh_token = token_data.get('refresh', "")

        url = reverse("users:auth-logout")
        data = {"refresh_token": refresh_token}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)


class EmployeeTestCase(UserBaseTestCase):
    def test_employee_creation(self):
        """
        Ensure we can create a employee with user.
        """
        data = {
            "employee_id": "employee10",
            "user": {
                "username": "employee10",
                "password": "bs23",
                "password2": "bs23",
                "email": "employee10@gmail.com",
                "first_name": "Employee",
                "last_name": "10"
            }
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.post(self.employee_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
