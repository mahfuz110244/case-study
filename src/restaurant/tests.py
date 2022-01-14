import json
import tempfile
from datetime import date

from PIL import Image
from rest_framework import status

from restaurant.models import Menu
from users.tests import UserBaseTestCase


# Create your tests here.
class RestaurantTestCase(UserBaseTestCase):
    def test_restaurant_creation(self):
        """
        Ensure we can create a restaurant with manager user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.post(self.restaurant_url, self.restaurant_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_menu_creation(self):
        """
        Ensure we can create a menu for a restaurant.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.post(self.restaurant_url, self.restaurant_data, format='json')
        response_data = json.loads(response.content)['data']
        self.assertTrue("id" in response_data.keys())
        restaurant_id = response_data.get('id', "")

        # Get JWT token for this manager10
        manager_access_token = self.get_jwt_token(self.restaurant_data['manager'])

        # Test Menu Upload for this Restaurant with image
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        data = {
            "name": "Super Lunch 19",
            "description": "Vegetable, Rice, Chicken Curry, Fruits",
            "menu_date": date.today(),
            "restaurant": restaurant_id,
            "price": 250,
            "image": tmp_file
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + manager_access_token)
        response = self.client.post(self.menu_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_getting_today_menu(self):
        """
        Ensure we can get current day menu from two restaurant.
        """
        # Create 1st Restaurant
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.post(self.restaurant_url, self.restaurant_data, format='json')
        response_data = json.loads(response.content)['data']
        self.assertTrue("id" in response_data.keys())
        restaurant_id = response_data.get('id', "")

        # Get JWT token for this manager10
        manager_access_token = self.get_jwt_token(self.restaurant_data['manager'])

        # Create 2nd Restaurant
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.post(self.restaurant_url, self.restaurant_data_two, format='json')
        response_data = json.loads(response.content)['data']
        self.assertTrue("id" in response_data.keys())
        restaurant_id_two = response_data.get('id', "")

        # Get JWT token for this manager2
        manager_access_token_two = self.get_jwt_token(self.restaurant_data_two['manager'])

        # Test Menu Upload for 1st Restaurant with image
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        menu_data = {
            "name": "Super Lunch 19",
            "description": "Vegetable, Rice, Chicken Curry, Fruits",
            "menu_date": date.today(),
            "restaurant": restaurant_id,
            "price": 250,
            "image": tmp_file
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + manager_access_token)
        response = self.client.post(self.menu_url, menu_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        image1 = Image.new('RGB', (100, 100))
        tmp_file1 = tempfile.NamedTemporaryFile(suffix='.jpg')
        image1.save(tmp_file1)
        tmp_file1.seek(0)
        menu_data_two = {
            "name": "Super Exclusive Lunch 19",
            "description": "Vegetable, Rice, Chicken Curry, Fruits",
            "menu_date": date.today(),
            "restaurant": restaurant_id_two,
            "price": 350,
            "image": tmp_file1
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + manager_access_token_two)
        response = self.client.post(self.menu_url, menu_data_two, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get today menu for a employee
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.employee_access_token)
        response = self.client.get(self.menu_view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Menu.objects.count(), 2)
