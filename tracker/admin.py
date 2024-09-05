from django.contrib import admin
from .models import Expense, MonthlyBudget

admin.site.register(Expense)
admin.site.register(MonthlyBudget)
