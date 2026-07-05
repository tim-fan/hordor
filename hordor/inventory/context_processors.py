def readonly_visitor(request):
    return {'is_readonly_visitor': getattr(request, 'is_readonly_visitor', False)}
