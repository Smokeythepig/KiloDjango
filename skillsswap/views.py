from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from .models import Skill, Expense


def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skillsswap/skill_list.html', {'skills': skills})


@login_required
def dashboard(request):
    skills = Skill.objects.all()

    category_filter = request.GET.get('category')

    if category_filter:
        skills = skills.filter(category=category_filter)

    total_skills = skills.count()
    category_totals = skills.values('category').annotate(count=Count('category'))

    return render(request, 'skillsswap/dashboard.html', {
        'total_skills': total_skills,
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


class ExpenseListView(ListView):
    model = Expense
    template_name = 'skillsswap/expense_list.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense_list = self.get_queryset()

        total = 0
        for item in expense_list:
            total += item.amount

        context['total_spending'] = total
        return context


class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswap/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswap/expense_form.html'
    success_url = reverse_lazy('expense_list')


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'skillsswap/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')