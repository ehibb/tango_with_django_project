from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # Constructs dictionary to pass to template engine as context
    # The key boldmessage matches to {{ boldmessage}} in the template
    context_dict = {'boldmessage' : 'Crunchy, creamy, cookie, candy, cupcake!'}
    
    # Return rendered response to send to client
    # Makes use of shortcut function for simplification
    # First parameter is template to be used
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')