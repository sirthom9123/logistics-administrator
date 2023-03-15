from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
import textwrap

class AdditionalHelpers(models.TextChoices):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3

class MyOffice(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=355)
    cost_per_kilo = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(1)], default=1.0)
    lat = models.CharField(max_length=100)
    lng = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.name} address {self.address}'
    

class Measurement(models.Model):
    location = models.CharField(max_length=355)
    destination = models.CharField(max_length=355)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    l_lat = models.CharField(max_length=100, null=True)
    l_lng = models.CharField(max_length=100, null=True)
    d_lat = models.CharField(max_length=100, null=True)
    d_lng = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Distance from {self.location} to {self.destination} is {self.distance} km"


class AdditionalInfo(models.Model):
    customer_code = models.CharField(max_length=10, blank=True, unique=True) 
    location = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=10 ,null=True)
    pickup_date = models.DateTimeField(null=True)
    additional_helpers = models.CharField(max_length=3, choices=AdditionalHelpers.choices, default=AdditionalHelpers.ZERO)
    floors = models.CharField(max_length=3, default=0)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta: 
        verbose_name_plural = 'Customer'
    
    def __str__(self):
        return f'{self.first_name} is moving on {self.pickup_date}'
    
    
    def get_absolute_url(self):
        return reverse("single_order", kwargs={"pk": self.pk})
    
    