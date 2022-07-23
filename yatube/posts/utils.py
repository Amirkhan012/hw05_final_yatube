from django.core.paginator import Paginator


PAGINATE_BY = 10


def paginate(request, post_list):
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
