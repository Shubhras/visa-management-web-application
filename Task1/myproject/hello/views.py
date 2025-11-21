from django.http import HttpResponse

# Create your views here.
def hello_view(request):
    print("hello django")
    return HttpResponse("Hello django")