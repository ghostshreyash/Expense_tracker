# tracker/urls.py
from django.contrib import admin
from django.urls import path,include
from .views import home, signup, user_login, expense_list, user_logout, expenses, charts, monthly_budget, add_expense, edit_expense, delete_expense, add_monthly_budget, edit_monthly_budget, clear_monthly_budget, charts_and_statistics_view

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('expenses/', expense_list, name='expense_list'),
    path('your-new-path/', expenses, name='expenses'),  
    path('monthly_budget/', monthly_budget, name='monthly_budget'),
    path('charts-and-statistics/', charts_and_statistics_view, name='charts_and_statistics'),
    path('add_expense/', add_expense, name='add_expense'),
    path('edit_expense/<int:expense_id>/', edit_expense, name='edit_expense'),
    path('delete_expense/<int:expense_id>/', delete_expense, name='delete_expense'),
    path('add_monthly_budget/', add_monthly_budget, name='add_monthly_budget'),
    path('edit_monthly_budget/<int:monthly_budget_id>/', edit_monthly_budget, name='edit_monthly_budget'),
    path('clear_monthly_budget/', clear_monthly_budget, name='clear_monthly_budget'),
    # Add more URL patterns as needed
]
