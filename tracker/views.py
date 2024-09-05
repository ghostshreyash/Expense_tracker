from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Sum, Avg, Count
from django.db.models.functions import ExtractMonth
from django.db import IntegrityError, models
from datetime import datetime, timedelta
from .forms import SignUpForm, LoginForm, ExpenseForm, MonthlyBudgetForm
from .models import Expense, MonthlyBudget


@login_required
def home(request):
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Retrieve or create MonthlyBudget for the user
    try:
        monthly_budget, _ = MonthlyBudget.objects.get_or_create(user=request.user, defaults={'amount': 0.0})
        is_monthly_budget_set = monthly_budget.amount > 0  # Check if monthly budget is set
    except IntegrityError:
        # Handle the case where an IntegrityError occurs (user already has a monthly budget)
        monthly_budget = MonthlyBudget.objects.get(user=request.user)
        is_monthly_budget_set = monthly_budget.amount > 0

    expense_form = ExpenseForm()

    return render(request, 'tracker/home.html', {
        'is_authenticated': request.user.is_authenticated,
        'expenses': recent_expenses,
        'total_expenses': total_expenses,
        'monthly_budget': monthly_budget,
        'expense_form': expense_form,
        'is_monthly_budget_set': is_monthly_budget_set,  # Add this line
        'show_add_monthly_budget_button': not is_monthly_budget_set,
    })

@login_required
def monthly_budget(request):
    user = request.user
    monthly_budget, created = MonthlyBudget.objects.get_or_create(user=user)

    if request.method == 'POST':
        monthly_budget_form = MonthlyBudgetForm(request.POST, instance=monthly_budget)
        if monthly_budget_form.is_valid():
            monthly_budget_form.save()
    else:
        monthly_budget_form = MonthlyBudgetForm(instance=monthly_budget)

    return render(request, 'tracker/monthly_budget.html', {
        'user': user,
        'monthly_budget': monthly_budget,
        'monthly_budget_form': monthly_budget_form,
    })

@login_required
def add_monthly_budget(request):
    user = request.user
    try:
        # Try to get the existing monthly budget for the user
        monthly_budget = MonthlyBudget.objects.get(user=user)
    except MonthlyBudget.DoesNotExist:
        # If it doesn't exist, create a new one
        monthly_budget = MonthlyBudget(user=user)

    if request.method == 'POST':
        monthly_budget_form = MonthlyBudgetForm(request.POST, instance=monthly_budget)
        if monthly_budget_form.is_valid():
            try:
                monthly_budget_form.save()
                return redirect('home')  # Redirect to home after saving the monthly budget
            except IntegrityError:
                # Handle the case where an IntegrityError occurs (user already has a monthly budget)
             return render(request, 'tracker/monthly_budget.html', {
                'user': user,
                'monthly_budget': monthly_budget,
                'monthly_budget_form': monthly_budget_form,
                'error_message': 'Monthly budget already exists for this user.'
            })

    else:
        monthly_budget_form = MonthlyBudgetForm(instance=monthly_budget)

    return render(request, 'tracker/monthly_budget.html', {
        'user': user,
        'monthly_budget': monthly_budget,
        'monthly_budget_form': monthly_budget_form,
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()

    return render(request, 'tracker/add_expense.html', {'form': form})

@login_required
def expense_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Set default values for start_date and end_date if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # Parse date strings to datetime objects
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Filter expenses based on date range and order by date in descending order
    expenses = Expense.objects.filter(user=request.user, date__range=[start_date_obj, end_date_obj]).order_by('-date')

    # Calculate total expense for the selected date range
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'tracker/expense_list.html', {
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
        'total_expense': total_expense,
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def charts(request):
    # Your view logic for displaying charts and statistics
    return render(request, 'tracker/charts_and_statistics.html')

def expenses(request):
    # Your view logic for displaying expenses
    return render(request, 'tracker/expense_list.html')

def charts_and_statistics_view(request):
    # Retrieve user's expenses
    expenses = Expense.objects.filter(user=request.user)

    # Calculate average monthly expense
    average_monthly_expense = calculate_average_monthly_expense()

    # Calculate monthly expense statistics
    monthly_expense_statistics = calculate_monthly_expense_statistics(request.user)

    # Calculate expenses by category
    expenses_by_category = expenses.values('category').annotate(
        total_amount=Sum('amount'),
        expense_count=Count('id')
    ).order_by('-total_amount')

    # Additional statistics
    total_expenses = expenses.aggregate(sum_expense=Sum('amount'))['sum_expense']
    biggest_expense = expenses.order_by('-amount').first()
    smallest_expense = expenses.order_by('amount').first()

    context = {
        'expenses_by_category': expenses_by_category,
        'monthly_expense_statistics': monthly_expense_statistics,
        'average_monthly_expense': average_monthly_expense,
        'total_expenses': total_expenses,
        'biggest_expense': biggest_expense,
        'smallest_expense': smallest_expense,
    }

    return render(request, 'tracker/charts_and_statistics.html', context)

def calculate_monthly_expense_statistics(user):
    # Your logic to calculate monthly expense statistics
    # Example: Calculating average monthly expense
    average_monthly_expense = Expense.objects.filter(user=user).aggregate(models.Avg('amount'))['amount__avg'] or 0

    # You can include more statistics as needed
    return {
        'average_monthly_expense': average_monthly_expense,
        # Add more statistical data here
    }

def calculate_average_monthly_expense():
    # Assuming you have a model named Expense with 'amount' and 'date' fields
    # This function calculates the average monthly expense
    average_monthly_expense = Expense.objects.filter(date__isnull=False).annotate(
        month=ExtractMonth('date')
    ).values('month').annotate(
        avg_expense=Avg('amount')
    ).aggregate(Avg('avg_expense'))

    return average_monthly_expense.get('avg_expense', 0)  # Return 0 if there are no expenses

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'tracker/edit_expense.html', {'form': form, 'expense': expense})

def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')

    return render(request, 'tracker/delete_expense.html', {'expense': expense})

@login_required
def edit_monthly_budget(request, monthly_budget_id):
    monthly_budget = get_object_or_404(MonthlyBudget, id=monthly_budget_id, user=request.user)

    if request.method == 'POST':
        form = MonthlyBudgetForm(request.POST, instance=monthly_budget)
        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = MonthlyBudgetForm(instance=monthly_budget)

    return render(request, 'tracker/edit_monthly_budget.html', {'form': form, 'monthly_budget': monthly_budget})

@login_required
def clear_monthly_budget(request):
    user = request.user
    try:
        monthly_budget = MonthlyBudget.objects.get(user=user)
        monthly_budget.delete()  # Delete the monthly budget
        messages.success(request, 'Monthly budget cleared successfully.')
    except MonthlyBudget.DoesNotExist:
        messages.warning(request, 'No monthly budget found.')

    # Redirect to home, and the home view will handle whether to show the "Monthly Budget Not Set" message
    return redirect('home')
