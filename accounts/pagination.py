from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
import math

class UserPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'records'
    page_query_param = 'page'
    max_page_size = 30

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        total_pages = math.ceil(count/self.page_size)
        print(self.request.user.pk)
        return Response(OrderedDict([
             ('count', self.page.paginator.count),
             ('total_pages', total_pages),
             ('countItemsOnPage', self.page_size),
             ('current', self.page.number),
             ('next', self.get_next_link()),
             ('previous', self.get_previous_link()),
             ('results', data)
         ]))