from django.http import HttpResponse
from django.template import loader

def home(request):

    template = loader.get_template('landlord/home.html')
    context = {
                'error_message': "hello"
    }
    return HttpResponse(template.render(context, request))

