from django.shortcuts import render, redirect #render generates html pages, redirect sends users to diff URL
from django.contrib.auth.decorators import login_required #ensures only logged-in users can see specific pages #for functions
from django.contrib.auth.mixins import LoginRequiredMixin #for classes
from django.db.models import Count, Sum #allow calculation of totals directly in database
from django.views.generic import ListView, CreateView, UpdateView, DeleteView #django blueprints that allow showing list/form
#without much code
from django.urls import reverse_lazy #
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import date
import csv
import json
import io #the above three handle file uploads
import requests #fetch live exchange rates from external API

from .models import Skill, Expense


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skillsswap/skill_list.html', {'skills': skills})


@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    # gets all expenses for the logged-in user

    category_totals = expenses.values('category').annotate(total=Sum('amount')).order_by('category')
    # groups expenses by category and sums the amounts (aggregation)

    total_spending = expenses.aggregate(total=Sum('amount'))['total'] or 0
    # calculates total spending across all expenses (aggregation)

    total_expenses = expenses.count()
    # counts total number of expenses

    return render(request, 'skillsswap/dashboard.html', {
        'total_spending': total_spending,
        'total_expenses': total_expenses,
        'category_totals': category_totals,
    })
# handles aggregation: calculates totals and groups data for display


class ExpenseForm(forms.ModelForm):
    class Meta:  #connects the form to the Expense model and picks the fields to show
        model = Expense 
        fields = ['date', 'amount', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self): #logic to prevent negative numbers or zeroes.
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError("The amount must be greater than zero.")
        return amount

    def clean_date(self): #logic to prevent expenses from being logged for days that don't exist yet.
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date > date.today():
            raise ValidationError("You cannot log an expense for a future date.")
        return selected_date


class ExpenseListView(LoginRequiredMixin, ListView): #inherits from LoginRequiredMixIn for security, ListView for function
    model = Expense #tells django which database teable to pull data from
    template_name = 'skillsswap/expense_list.html' #specifies which html file to use to render the data
    context_object_name = 'expenses' #renames the list of data being passed to html. instead of using the default
    #object_list, can loop through expense in expenses

    def get_queryset(self): #allows more specification on which expenses can be shown on site
        #overrides default of allowing everything to be displayed for more filtering below:
        qs = Expense.objects.filter(user=self.request.user) #filters database so user only sees the expenses linked to 
        #their own account, not others (security reason)
        category = self.request.GET.get('category') #this and the next two lines looks at URL for search parameters.
        #pulls category name from url and store in variable
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if category:  #if user provides a category, refine list. __iexact makes search case-insensitive.
            qs = qs.filter(category__iexact=category)

        if date_from and date_to:
            if date_from > date_to:
                messages.error(self.request, "The 'From' date must be earlier than the 'To' date.")
                return qs.none()  # Return an empty queryset
            qs = qs.filter(date__range=[date_from, date_to])
            
        elif date_from:
            qs = qs.filter(date__gte=date_from) #__gte is greater than or equal to, filters for expenses
            #on or after the chosen start date
        elif date_to:
            qs = qs.filter(date__lte=date_to) #__lte is less than or equal to, filters for expenses
            #on or before the chosen end date
        return qs.order_by('-date') #returns final filtered list, - in -date sorts in reverse chronological order (newest first)

    def get_context_data(self, **kwargs): #allows us to send extra info to html page that isn't just the expense list
        #ex. if wanted to pass total sum of filtered results to template, etc.
        context = super().get_context_data(**kwargs) #
        qs = self.get_queryset() 
        context['total_spending'] = qs.aggregate(total=Sum('amount'))['total'] or 0
        context['category_filter'] = self.request.GET.get('category', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView): #uses CreateView to automatically handle displaying a blank
    #form and saving the data.
    model = Expense #links the view to the Expense model and the ExpenseForm
    form_class = ExpenseForm
    template_name = 'skillsswap/expense_form.html' #links to this url
    success_url = reverse_lazy('expense_list') #tells django where to send user after they click 'save', here, back
    #to main list
    #expense_list is the name i gave the url in urls.py
    #reverse_lazy makes it so that django will automatically direct to the new url path if I edit the name in urls.py
    #reverse_lazy is a tool handling URL routing, waits to look up url until is it needed (ex. after user clicks
    #submit and form is processed), works with class based views (normally reverse() is used but might look
    #up url before url config. finishes loading, potential crash
    #
    

    def form_valid(self, form): #runs before data is saved to database, method that runs after data check but before saving.
        #method inside CreateView
        form.instance.user = self.request.user #automatically sets the owner of the expense to the person logged in
        #since Expense model requires a user line (in models.py, save would fail unless defined here
        return super().form_valid(form)  #triggers save to database


class ExpenseUpdateView(LoginRequiredMixin, UpdateView): #logic for editing an existing expense
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswap/expense_form.html' #
    success_url = reverse_lazy('expense_list')

    def get_queryset(self): 
        return Expense.objects.filter(user=self.request.user)
#security line, if user manually tries to type url such as /edit/99/, django will check if it belongs to them,
#otherwise 404 not found error


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'skillsswap/expense_confirm_delete.html' #uses specific template to confirm with user if they really
    #want to remove the data
    success_url = reverse_lazy('expense_list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user) #same security as line 134


# --- Currency Conversion ---

EXCHANGE_API_URL = 'https://open.er-api.com/v6/latest/USD'

@login_required
def currency_conversion(request):
    total_usd = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    converted = None
    target_currency = ''
    error = None

    if request.method == 'POST':
        target_currency = request.POST.get('currency', '').upper().strip()
        try:
            response = requests.get(EXCHANGE_API_URL, timeout=5)
            response.raise_for_status()
            rates = response.json().get('rates', {})
            if target_currency in rates:
                converted = round(float(total_usd) * rates[target_currency], 2)
            else:
                error = f"Currency '{target_currency}' not found."
        except requests.RequestException:
            error = "Currency conversion service is unavailable. Please try again later."

    return render(request, 'skillsswap/currency_conversion.html', {
        'total_usd': total_usd,
        'converted': converted,
        'target_currency': target_currency,
        'error': error,
    })


# --- File Import ---

class ImportForm(forms.Form):
    file = forms.FileField(label='CSV or JSON file')

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        name = uploaded.name.lower()
        if not (name.endswith('.csv') or name.endswith('.json')):
            raise ValidationError(
                f'"{uploaded.name}" is not accepted. Only .csv and .json files are supported.'
            )
        return uploaded


@login_required
def import_expenses(request):
    imported = 0
    skipped = 0
    errors = []

    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = request.FILES['file']
            filename = uploaded.name.lower()
            try:
                content = uploaded.read().decode('utf-8')
                if filename.endswith('.csv'):
                    imported, skipped, errors = _import_csv(request.user, content)
                else:
                    imported, skipped, errors = _import_json(request.user, content)
            except Exception as e:
                errors = [f'Could not read file: {e}']
    else:
        form = ImportForm()

    return render(request, 'skillsswap/import.html', {
        'form': form,
        'imported': imported,
        'skipped': skipped,
        'errors': errors,
    })


def _parse_row(user, row):
    date_val = row.get('date', '').strip()
    amount_val = row.get('amount', '').strip()
    category = row.get('category', '').strip()
    description = row.get('description', '').strip()

    if not date_val or not amount_val or not category:
        raise ValueError("Missing required field (date, amount, or category).")

    amount = float(amount_val)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    parsed_date = date.fromisoformat(date_val)
    if parsed_date > date.today():
        raise ValueError("Date cannot be in the future.")

    return Expense(user=user, date=parsed_date, amount=amount, category=category, description=description)


def _import_csv(user, content):
    imported, skipped, errors = 0, 0, []
    reader = csv.DictReader(io.StringIO(content))
    for i, row in enumerate(reader, start=2):
        try:
            expense = _parse_row(user, row)
            expense.save()
            imported += 1
        except Exception as e:
            skipped += 1
            errors.append(f"Row {i}: {e}")
    return imported, skipped, errors


def _import_json(user, content):
    imported, skipped, errors = 0, 0, []
    try:
        data = json.loads(content)
        if not isinstance(data, list):
            return 0, 0, ['JSON file must contain a list of expense objects.']
    except json.JSONDecodeError as e:
        return 0, 0, [f'Invalid JSON: {e}']

    for i, row in enumerate(data, start=1):
        try:
            if not isinstance(row, dict):
                raise ValueError("Each item must be an object.")
            expense = _parse_row(user, {k: (str(v) if v is not None else '') for k, v in row.items()})
            expense.save()
            imported += 1
        except Exception as e:
            skipped += 1
            errors.append(f"Item {i}: {e}")
    return imported, skipped, errors


# --- Registration ---

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
