# tracker/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    is_scheduled = models.BooleanField(default=False)
    scheduled_date = models.DateField(null=True, blank=True)
    
    CATEGORY_CHOICES = [
        ('monthly_bills', 'Monthly Bills'),
        ('electronics', 'Electronics'),
        ('petrol', 'Petrol'),
        ('groceries', 'Groceries'),
        ('online_shopping', 'Online Shopping'),
        ('miscellaneous', 'Miscellaneous'),
    ]
    
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    source = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username}'s Expense - {self.amount}"
    
class MonthlyBudget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s Monthly Budget"
