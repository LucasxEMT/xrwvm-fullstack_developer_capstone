from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

# Car Make model
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# Car Model model
class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    # Dealer ID - references an external dealer in Cloudant or elsewhere
    dealer_id = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=100)

    # Car type choices
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    HATCHBACK = 'Hatchback'
    COUPE = 'Coupe'
    CAR_TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (HATCHBACK, 'Hatchback'),
        (COUPE, 'Coupe'),
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default=SUV)

    # Year as an Integer (range 2015–2023)
    year = models.IntegerField(
        validators=[
            MinValueValidator(2015),
            MaxValueValidator(2023)
        ],
        default=2023
    )

    def __str__(self):
        return f"CarModel: {self.name} / Make: {self.make.name} / Type: {self.type}"
