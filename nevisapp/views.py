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

#predict analysis
import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
import numpy as np

from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .models import News

import requests
import json

def coba(request):
    return JsonResponse({'test': "hallo"})

def get_data_from_api(request):
    api_url = 'http://127.0.0.1:8000/nevisapp/al_pred/'  # Replace this with your API endpoint
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Failed to fetch data from API'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_pred_al(request):
    # Change 'your_excel_file.xlsx' to the path of your Excel file
    excel_file_path = os.path.join(settings.BASE_DIR, 'dataset', 'test.xlsx')

    # Read data from Excel file using pandas
    df = pd.read_excel(excel_file_path)
    # Convert 'Date' column to datetime type
    df['Date'] = pd.to_datetime(df['Date'])

    data = df[['Date', 'Aluminium Price']].rename(columns={'Date': 'ds', 'Aluminium Price': 'y'})
    data.set_index('ds', inplace=True)

    model = ExponentialSmoothing(data, seasonal='add', seasonal_periods=12)
    fitted_model = model.fit()
    predictions = fitted_model.forecast(steps=10)
    df_pred = pd.DataFrame(list(predictions.items()), columns=['Date', 'Value'])
    merged_df = pd.merge(df[['Date','Aluminium Price']], df_pred, on='Date', how='outer')
    merged_df['Aluminium Price'] = merged_df['Aluminium Price'].fillna(merged_df['Value'])
    merged_df.drop(columns=['Value'], inplace=True)

    # Convert 'Date' column to string
    merged_df['Date'] = merged_df['Date'].dt.strftime('%Y-%m-%d')
    merged_df.rename(columns={'Date': 'date', 'Aluminium Price': 'aluminium_price'}, inplace=True)

    merged_df_json = merged_df.to_json(orient='records', double_precision=15)

    # Return the JSON response with column names
    response_data = {"data": json.loads(merged_df_json)}
    return JsonResponse(response_data)
    # return render(request, 'nevisapp/merged_df.html', {'merged_df': json.loads(merged_df_json)})
    # Pass the data to the template
    # return render(request, 'nevisapp/merged_df.html', {'merged_df_json': merged_df_json})

def al_predict(request):
    return render(request, 'nevisapp/merged_df.html')


def import_and_return_json(request):
    # Change 'your_excel_file.xlsx' to the path of your Excel file
    excel_file_path = os.path.join(settings.BASE_DIR, 'dataset', 'test.xlsx')

    # Read data from Excel file using pandas
    df = pd.read_excel(excel_file_path)

    # # Convert dataframe to JSON
    # data_json = df.to_json(orient='records')
    # # Remove leading and trailing double quotes
    # data_string = data_json.strip('"')

    # # Convert to JSON
    # data_json = json.loads(data_string)

    # # Return the JSON response
    # return JsonResponse({"results": data_json})

    # Convert the JSON response to a DataFrame
    # data = {
    #     "Date": [1293840000000, 1296518400000, 1298937600000, 1301616000000],
    #     "Aluminium Price": [2439.7, 2515.26, 2555.5, 2667.4166666667],
    #     "Copper Price": [9533.2, 9884.9, 9503.3586956522, 9482.75],
    #     "BADI -2": [2321.3181818182, 2030.9444444444, 1401.8, 1181.1],
    #     "MJP": [112.5, 112.5, 113, 114],
    #     "USD Index": [79.1553809524, 77.7776, 76.2876521739, 74.6897619048],
    #     "AL Prod (Global)": [3758.482821, 3416.918966, 3788.014108, 3800.103276],
    #     "AL Cons (Global)": [3646.5591542059, 3210.0681146571, 3674.2978401862, 3823.5741200196],
    #     "Aluminium stocks": [11886.3473095413, 12093.1981608842, 12206.9144286979, 12183.4435846784],
    #     "Alumina Index": [378.2975, 392.4375, 402.1475, 410.37],
    #     "Oil Prices": [97, 104, 115, 123]
    # }

    # df = pd.DataFrame(data)

    # Define features and target
    X = df.drop(columns=["Aluminium Price"])
    y = df["Aluminium Price"]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Calculate Mean Squared Error
    mse = np.mean((predictions - y_test) ** 2)
    return JsonResponse({"mse": mse})


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

