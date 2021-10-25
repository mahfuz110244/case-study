import logging
from datetime import date

from base.documentation import jwt_header
from base.permissions import IsEmployee, IsManager
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_condition import Or
from rest_framework import filters, status, viewsets
from rest_framework.decorators import parser_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from restaurant.models import Menu
from restaurant.serializers import MenuListSerializer, MenuSerializer

logger = logging.getLogger('voting_app')


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[jwt_header]))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(manual_parameters=[jwt_header]))
@method_decorator(name='create', decorator=swagger_auto_schema(manual_parameters=[jwt_header]))
@parser_classes([MultiPartParser, ])
class MenuViewSet(viewsets.ModelViewSet):
    """
    Uploading menu for restaurant (There should be a menu for each day)
    """
    permission_classes = [Or(IsManager, IsAdminUser)]
    authentication_classes = [JWTAuthentication]
    queryset = Menu.objects.all().select_related('restaurant', 'restaurant__manager')
    serializer_class = MenuSerializer

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'restaurant__name']
    filter_fields = ['name', 'menu_date', 'restaurant__name']
    http_method_names = ['get', 'post']

    # def get_queryset(self):
    #     if IsAdminUser.has_permission(self, request=self.request, view=self.get_view_name()):
    #         return super().get_queryset()
    #     elif IsEmployee.has_permission(self, request=self.request, view=self.get_view_name()):
    #         if self.request.query_params.get('menu_date'):
    #             return super().get_queryset()
    #         raise PermissionDenied()
    #     return super().get_queryset().filter(restaurant__manager=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsManager]
        elif self.action == 'list':
            permission_classes = [Or(IsAdminUser, IsManager, IsEmployee)]
        else:
            permission_classes = [Or(IsAdminUser, IsManager)]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return MenuListSerializer
        return MenuSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(manual_parameters=[jwt_header]))
class MenuList(APIView):
    permission_classes = [Or(IsEmployee, IsAdminUser)]
    authentication_classes = [JWTAuthentication]
    """
    An API endpoint for Getting current day menu
    """
    def get(self, request):
        try:
            queryset = Menu.objects.filter(menu_date=date.today()).select_related('restaurant')
            serializer_context = {
                'request': request
            }
            serializer = MenuListSerializer(queryset, context=serializer_context, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in {request.resolver_match.view_name}, error: {e}")
            return Response({'message': "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
