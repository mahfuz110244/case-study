from django.urls import path
from rest_framework import routers

from restaurant.views import MenuViewSet, RestaurantViewSet

app_name = 'restaurant'
router = routers.SimpleRouter()
router.register(r'menu', MenuViewSet, 'restaurant-menu')
router.register(r'', RestaurantViewSet, 'restaurant')

urlpatterns = router.urls
