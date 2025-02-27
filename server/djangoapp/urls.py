from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # path for login
    path('login', views.login_user, name='login'),

    # path for get_cars
    path('get_cars', views.get_cars, name='get_cars'),
    
    # Add other routes as needed, e.g. logout, registration, etc.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
