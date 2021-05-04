from django.core.paginator import Paginator


def post_paginator(request, post_list, count=10):
    paginator = Paginator(post_list, count)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator
