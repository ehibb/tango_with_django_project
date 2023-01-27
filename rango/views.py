from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def register(request):
    #Boolean value telling template if registration was successful
    registered = False
    
    #If HTTP POST we process form data:
    if request.method == 'POST':
        #Get info from raw form information
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        #If both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            #Save user form data to database
            user = user_form.save()
            
            #Hash password with set_password method and update user object
            user.set_password(user.password)
            user.save()
            
            #Dealing with UserProfile instance; set commit = False to delay saving model
            #We must set user attributes
            profile = profile_form.save(commit = False)
            profile.user = user
            
            #Check for profile picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            #Now save profile
            profile.save()
            
            #Indicates registration was successful
            registered = True
            
        else:
            print(user_form.errors, profile_form.errors)
        
    else:
        #If not HTTP post
        #Render form using two (blank) ModelForm instances
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    #Return template depending on context
    return render(request, 'rango/register.html', context= {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    #If request is HTTP POST, attempt to pull out relevant info
    if request.method == 'POST':
        #Get username and password from login form
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        #Django magic used to authenticate username/password, returning User object if it is
        user = authenticate(username=username, password=password)
        
        #If we have a User object (details are correct)
        if user:
            #Check if active
            if user.is_active:
                #Log user in and redirect to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            #If inactive
            else:
                return HttpResponse("Your Rango account is disabled.")
                
        #If details are bad        
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    #If not a HTTP POST, show login form
    else:
        #No need to use a context dictionary
        return render(request, 'rango/login.html')


#To ensure only those logged in can log out           
@login_required
def user_logout(request):
    #Simply log out
    logout(request)
    #Take user back to homepage
    return redirect(reverse('rango:index'))
    


    
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


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
    
@login_required
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
    
@login_required    
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