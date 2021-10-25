from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.views import (ChangePasswordView, EmployeeViewSet, LogoutView,
                         RegisterView)

router = routers.SimpleRouter()
router.register(r'employee', EmployeeViewSet, 'employee')

app_name = 'users'
auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('logout/', LogoutView.as_view(), name='auth-logout')
]

user_urlpatterns = router.urls

urlpatterns = auth_urlpatterns + user_urlpatterns
