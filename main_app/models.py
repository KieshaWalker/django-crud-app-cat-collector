from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

# A tuple of 2-tuples added above our models
MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)
class Cat(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly declare for IDE support
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    toys = models.ManyToManyField('Toy')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        # Use the 'reverse' function to dynamically find the URL for viewing this cat's details
        return reverse('cat-detail', kwargs={'cat_id': self.id})    

class Feeding(models.Model):
    date = models.DateField()
    meal = models.CharField(
        max_length=1,
        choices=MEALS,
        default=MEALS[0][0]
    )
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name= 'feedings')

    def __str__(self):
        return f"{self.get_meal_display()} on {self.date}" # type: ignore
    
    class Meta:
        ordering = ['-date']

class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('toy-detail', kwargs={'pk': self.id})
