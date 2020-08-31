from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

class EsPagination(pagination.LimitOffsetPagination):
    default_limit = 25
    def get_paginated_response(self, data):
        d = {
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.count,
        }
        if (isinstance(data, dict)):
            d['lastel'] = data['lastel']
            d['results'] = data['results'] 
            newLastEl = str(data['lastel'][0]) + "," + str(data['lastel'][1])
            d['links']['next'] = replace_query_param(d['links']['next'],'lastel', newLastEl)
            # One could also remove the automatically generated '&offset=XX' from the link to avoid confusion
            d['previous'] = None
        else:
            d['results'] = data
        return Response(d)

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {  
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_count': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

class CustomSearchPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': data['counts'],
            'page_count': data['page_counts'],
            'current_page': self.page.number,
            'results': {i:data[i] for i in data if (i!='counts' and i!='page_counts')}
        })

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except:
            return None

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

class CustomAssociationsPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': data['count'],
            'page_count': data['page_count'],
            'current_page': self.page.number,
            'results': {i:data[i] for i in data if (i!='count' and i!='page_count')}
        })

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except:
            return None

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)