from django.http import HttpResponse

def index(request):
    return HttpResponse("inventory index")