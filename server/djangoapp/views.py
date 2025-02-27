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
# (Optional) get_dealerships, get_dealer_reviews, etc.

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
