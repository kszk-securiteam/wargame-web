from search_views.filters import BaseFilter


class UserFilter(BaseFilter):
    search_fields = {
        'name': ['username']
    }