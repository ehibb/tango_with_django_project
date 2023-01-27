from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def index(request):
    #Query database for list of ALL categories currently stored
    #Orders categories by likes in descencing order
    #Retrieves top 5, or all if there are less than 5 categories
    #Place the list in our context_dict dictionary which will be passed to the template engine
    category_list = Category.objects.order_by('-likes')[:5]
    
    #Similarly for pages, ordered by views in descending order
    page_list = Page.objects.order_by('-views')[:5]
    
    # Constructs dictionary to pass to template engine as context
    # The key boldmessage matches to {{ boldmessage}} in the template
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    # Return rendered response to send to client
    # Makes use of shortcut function for simplification
    # First parameter is template to be used
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    # Create empty context dictionary to pass to template rendering engine
    context_dict = {}
    
    try:
        #Try to get the category name slug for the given name
        #.get() raises a DoesNotExist if it cannot find it
        #i.e. the .get() function returns a model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)
        
        #Retrieves all pages associated with category
        pages = Page.objects.filter(category=category)
        
        #Add results list to template context under pages
        context_dict['pages'] = pages
        
        #Add category to context dictionary
        #This is used to verify the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        #We get here if the category is not found
        #In this occasion we do nothing
        #The template will display 'no category' message for us
        context_dict['category'] = None
        context_dict['pages'] = None
    
    #Render response and return to client
    return render(request, 'rango/category.html', context=context_dict)
    
def add_category(request):
    form = CategoryForm()
    
    #HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        #Is form valid?
        if form.is_valid():
            form.save(commit=True)
            
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form': form})
    
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        
        
    #Can't add page to non-existant category
    if category is None:
        return redirect(reverse('rango:index'))
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views=0
                page.save()
                
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
                
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request,'rango/add_page.html', context=context_dict)