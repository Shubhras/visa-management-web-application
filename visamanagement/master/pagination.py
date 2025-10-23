from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "status": True,
            "statusCode": 200,
            "message": "Data retrieved successfully",
            "data": data,
            "pagination": {
                "currentPage": self.page.number,
                "limit": self.get_page_size(self.request),
                "totalItems": self.page.paginator.count,
                "totalPages": self.page.paginator.num_pages,
                "nextPage": self.page.has_next(),
                "previousPage": self.page.has_previous(),
            }
        })