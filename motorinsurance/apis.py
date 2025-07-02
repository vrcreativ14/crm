import datetime

from accounts.permissions import HasAdminRolePermission
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from insurers.models import Insurer
from motorinsurance.serializers import PolicySerializer, InsurerSerializer, ProductSerializer
from motorinsurance.models import Policy


class ListInsurersView(ListAPIView):
    permission_classes = [
        HasAdminRolePermission,
    ]

    serializer_class = InsurerSerializer

    def get_queryset(self):
        company = self.request.company
        available_products = company.available_motor_insurance_products.all()
        insurer_id = list(available_products.order_by('insurer_id').values_list('insurer_id', flat=True).distinct(
            'insurer_id'
        ))
        return Insurer.objects.filter(pk__in=insurer_id)


class ListProductsView(ListAPIView):
    permission_classes = [
        HasAdminRolePermission,
    ]

    serializer_class = ProductSerializer

    def get_queryset(self):
        company = self.request.company
        return company.available_motor_insurance_products.all()


class ListPoliciesView(ListAPIView):
    permission_classes = [
        HasAdminRolePermission,
    ]

    serializer_class = PolicySerializer

    def get_queryset(self):
        company = self.request.company

        created_on_start = self.request.query_params['min_creation_date']
        created_on_end = self.request.query_params['max_creation_date']

        created_on_start = datetime.datetime.strptime(created_on_start, '%Y-%m-%d')
        created_on_end = datetime.datetime.strptime(created_on_end, '%Y-%m-%d')

        if created_on_end < created_on_start:
            return Response('End date must be later than start date.', status=400)
        if (created_on_end - created_on_start).days > 31:
            return Response('This API can only return up to 31 days of data at a time.', status=400)

        return Policy.objects.filter(
            company=company,
            status=Policy.STATUS_ACTIVE,
            created_on__range=(created_on_start, created_on_end)
        )
