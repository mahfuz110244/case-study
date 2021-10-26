import json
import logging
import tempfile
from datetime import date, datetime

from django.conf import settings
from PIL import Image
from rest_framework import status

from restaurant.models import Menu
from users.tests import UserBaseTestCase

from .models import Vote

logger = logging.getLogger('voting_app')


# Create your tests here.
class VoteTestCase(UserBaseTestCase):
    def test_vote_result_today_menu(self):
        """
        Ensure employee can vote current day menu from two restaurant.
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
        response_data = json.loads(response.content)['data']
        self.assertTrue("id" in response_data.keys())
        menu_id = response_data.get('id', "")

        # Get today menu for a employee
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.employee_access_token)
        response = self.client.get(self.menu_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Menu.objects.count(), 1)

        vote_data = {
            "menu": menu_id
        }
        today_datetime = datetime.now()
        voting_deadline = today_datetime.replace(hour=settings.VOTING_LAST_HOUR, minute=0, second=0, microsecond=0)
        deadline_over = False
        if voting_deadline < today_datetime:
            deadline_over = True

        # Voting for employee1
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.employee_access_token)
        response = self.client.post(self.vote_url, vote_data, format='json')
        response_data = json.loads(response.content)
        logger.info(response_data)
        if deadline_over:
            self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        else:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Voting for employee2
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.employee_access_token_two)
        response = self.client.post(self.vote_url, vote_data, format='json')
        response_data = json.loads(response.content)
        logger.info(response_data)
        if deadline_over:
            self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        else:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # getting result for today votes
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.get(self.vote_result_url)
        response_data = json.loads(response.content)
        logger.info(response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if deadline_over:
            self.assertEqual(Vote.objects.count(), 0)
        else:
            self.assertEqual(Vote.objects.count(), 2)

        # publish result for today vote
        self.client.credentials(HTTP_AUTHORIZATION='Bearer  ' + self.admin_access_token)
        response = self.client.post(self.vote_result_publish_url)
        response_data = json.loads(response.content)
        logger.info(response_data)
        if deadline_over:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
