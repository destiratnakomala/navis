from django.shortcuts import render
from .forms import UserForm,UserProfileInfoForm
from django.http import JsonResponse

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.conf import settings
import os

from .models import News

import requests

def import_and_return_json(request):
    # Change 'your_excel_file.xlsx' to the path of your Excel file
    excel_file_path = os.path.join(settings.BASE_DIR, 'dataset', 'test.xlsx')

    # Read data from Excel file using pandas
    df = pd.read_excel(excel_file_path)

    # Convert dataframe to JSON
    data_json = df.to_json(orient='records')

    # Return the JSON response
    return JsonResponse(data_json, safe=False)


# Create your views here.
def index(request):
    return render(request,'nevisapp/index.html')

def dashboard(request):
    return render(request,'nevisapp/index.html')

def get_news(request):
    data = News.objects.all()
    data = {"results": data}
    return render(request, 'nevisapp/news.html', data)

def get_news_by_id(request, keywords):
    try:
        data = News.objects.filter(keywords=keywords)
        serialized_data = []
        for news in data:
            serialized_data.append({
                "id": news.id,
                "title": news.title,
                "source": news.source,
            })
        return JsonResponse(serialized_data, safe=False)
    except News.DoesNotExist:
        return JsonResponse({"error": "News not found"}, status=404)

def news_analysis(request):
    if request.method == 'POST':
        # First get the username and password supplied
        query = request.POST.get('query')

        # Set up the query parameters
        api_key = "e2a30aecb963d2caeb1fd6303c6c45ed641ec2df5a87afca772e7c0e63c37df7"
        engine = "google"

        # Construct the API URL
        url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&engine={engine}"

        # Send a GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # List to hold all the results
            results = []

            for dt in data['organic_results']:
                link = dt['link']
                # Check if a News instance with the same link already exists
                if not News.objects.filter(link=link).exists():
                    result = News()
                    result.title = dt['title']
                    result.link = link
                    result.redirect_link = dt['redirect_link']
                    result.displayed_link = dt['displayed_link']
                    result.favicon = dt['favicon']
                    result.snippet = dt['snippet']
                    result.snippet_highlighted_words = ''
                    result.source = dt['source']
                    result.save()
                    results.append(result)
            
            data = {"results": results}
            # Render the template with the results
            return render(request, 'nevisapp/news_analysis.html', data)
        else:
            # Handle the error
            print(f"Error: {response.status_code}")

    return render(request, 'nevisapp/news_analysis.html')
    

@login_required
def special(request):
    # Remember to also set login url in settings.py!
    # LOGIN_URL = '/basic_app/user_login/'
    return HttpResponse("You are logged in. Nice!")

@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))

def register(request):

    registered = False

    if request.method == 'POST':

        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        # Check to see both forms are valid
        if user_form.is_valid() and profile_form.is_valid():

            # Save User Form to Database
            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Now we deal with the extra info!

            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)

            # Set One to One relationship between
            # UserForm and UserProfileInfoForm
            profile.user = user

            # Check if they provided a profile picture
            if 'profile_pic' in request.FILES:
                print('found it')
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']

            # Now save model
            profile.save()

            # Registration Successful!
            registered = True

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors,profile_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request,'nevisapp/registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})

def user_login(request):

    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        # If we have a user
        if user:
            #Check it the account is active
            if user.is_active:
                # Log the user in.
                login(request,user)
                # Send the user back to some page.
                # In this case their homepage.
                return HttpResponseRedirect(reverse('index'))
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details supplied.")

    else:
        #Nothing has been provided for username or password.
        return render(request, 'nevisapp/login.html', {})


def get_analyze(request):

    if request.method == 'POST':
        # First get the username and password supplied
        query = request.POST.get('query')

        # Set up the query parameters
        api_key = "e2a30aecb963d2caeb1fd6303c6c45ed641ec2df5a87afca772e7c0e63c37df7"
        engine = "google"

        # Construct the API URL
        url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&engine={engine}"

        # Send a GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            for dt in data['organic_results']:
                result = News()

                # Set the attributes of the model instance
                result.title = dt['title']
                result.link = dt['url']
                result.redirect_link = dt['redirect_link']
                result.displayed_link = dt['displayed_link']
                result.favicon = dt['favicon']
                result.snippet = dt['snippet']
                result.snippet_highlighted_words = dt['snippet_highlighted_words']
                result.source = dt['source']

                # Save the model instance to the database
                result.save()
        else:
            # Handle the error
            print(f"Error: {response.status_code}")

