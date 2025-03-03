# Uncomment the required imports before adding the code

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from .restapis import get_request, analyze_review_sentiments, post_review
# Import your CarMake and CarModel
from .models import CarMake, CarModel

# OPTIONAL: If you want to auto-populate data when the DB is empty
from .populate import initiate

logger = logging.getLogger(__name__)

# Create a `login_user` view to handle sign in request
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data.get('userName')
    password = data.get('password')
    user = authenticate(username=username, password=password)

    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data["status"] = "Authenticated"
    return JsonResponse(response_data)

# (Optional) Create a `logout_request` view to handle sign out request
# (Optional) Create a `registration` view to handle sign up request

def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Create a `get_cars` view to list CarModels and their associated CarMakes
def get_cars(request):
    # Auto-populate if CarModel is empty
    if CarModel.objects.count() == 0:
        initiate()
    
    car_models = CarModel.objects.select_related('make')  # or 'make' if your FK field is named 'make'
    cars = []
    for cm in car_models:
        cars.append({
            "CarModel": cm.name,
            "CarMake": cm.make.name
        })
    return JsonResponse({"CarModels": cars})

def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
