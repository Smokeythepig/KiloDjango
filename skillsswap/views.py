from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import date
import csv
import json
import io
import requests

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

    category_totals = expenses.values('category').annotate(total=Sum('amount')).order_by('category')
    total_spending = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expenses.count()

    return render(request, 'skillsswap/dashboard.html', {
        'total_spending': total_spending,
        'total_expenses': total_expenses,
        'category_totals': category_totals,
    })


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError("The amount must be greater than zero.")
        return amount

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date > date.today():
            raise ValidationError("You cannot log an expense for a future date.")
        return selected_date


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'skillsswap/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user)
        category = self.request.GET.get('category')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if category:
            qs = qs.filter(category__iexact=category)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['total_spending'] = qs.aggregate(total=Sum('amount'))['total'] or 0
        context['category_filter'] = self.request.GET.get('category', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswap/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswap/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'skillsswap/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


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
                elif filename.endswith('.json'):
                    imported, skipped, errors = _import_json(request.user, content)
                else:
                    errors = ['Only .csv and .json files are supported.']
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
            expense = _parse_row(user, {k: str(v) for k, v in row.items()})
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
