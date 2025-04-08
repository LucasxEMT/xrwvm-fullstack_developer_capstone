import logging
import json

from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """
    Handle user login via JSON payload with 'userName' and 'password'.
    """
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data["status"] = "Authenticated"
    return JsonResponse(response_data)


def logout_request(request):
    """
    Handle user logout.
    """
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    """
    Handle user registration via JSON payload with
    'userName', 'password', 'firstName', 'lastName', and 'email'.
    """
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("{} is a new user".format(username))
    except Exception as err:
        logger.error("Unexpected error: %s", err, exc_info=True)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"userName": username, "error": "Already Registered"})


def get_cars(request):
    """
    Return list of cars from CarMake and CarModel. If empty, populate first.
    """
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    """
    Fetch dealerships. If state is 'All', fetch all; otherwise fetch by state.
    """
    logger.info("Called function get_dealerships")
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    base_url = (
        "https://lucas1234517-3030.theiadockernext-1-labs-prod-"
        "theiak8s-4-tor01.proxy.cognitiveclass.ai"
    )
    full_url = base_url + endpoint
    logger.info("Full URL used: %s", full_url)
    try:
        dealerships = get_request(endpoint)
        logger.info("Dealerships response: %s", dealerships)
    except Exception as e:
        logger.error("Error fetching dealerships: %s", e, exc_info=True)
        return JsonResponse({
            "status": 500,
            "error": "Error fetching dealerships"
        })
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """
    Get reviews for a given dealer_id, analyze sentiments, return JSON.
    """
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            if response and 'sentiment' in response:
                review_detail['sentiment'] = response['sentiment']
            else:
                review_detail['sentiment'] = "unknown"
        return JsonResponse({"status": 200, "reviews": reviews})
    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_details(request, dealer_id):
    """
    Get a single dealer's details using a dealer_id.
    """
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})


@csrf_exempt
def add_review(request):
    """
    Add a review if user is authenticated. POST data in JSON body.
    """
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as err:
            logger.error("Error posting review: %s", err, exc_info=True)
            return JsonResponse({"status": 401, "message": "Error in posting"})
    return JsonResponse({"status": 403, "message": "Unauthorized"})
