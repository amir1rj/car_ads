from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultSetPagination(PageNumberPagination):
    page_size = getattr(settings, 'PAGINATION_PAGE_SIZE', 1)


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'total_page': self.page.paginator.num_pages  # Add total_page field
        })
