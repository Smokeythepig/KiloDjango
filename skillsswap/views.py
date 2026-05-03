from django.shortcuts import render
from .models import Skill

def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skillsswap/skill_list.html', {'skills': skills})

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Expense
from .forms import ExpenseForm


from django import forms
from .models import Expense
from django.core.exceptions import ValidationError
from datetime import date

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        # Check if amount is None first to avoid errors if the field is empty
        if amount is not None and amount <= 0:
            raise ValidationError("The amount must be greater than zero.")
        return amount

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date > date.today():
            raise ValidationError("You cannot log an expense for a future date.")
        return selected_date

# LIST VIEW 
class ExpenseListView(ListView):
    model = Expense
    template_name = 'skillsswp/expense_list.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Get all the expenses being shown on the page
        expense_list = self.get_queryset()
        
        # 2. Manual calculation (Just like Checkpoint 2!)
        total = 0
        for item in expense_list:
            total += item.amount
            
        # 3. Pass it to the template
        context['total_spending'] = total
        return context


# CREATE VIEW
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswp/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def form_valid(self, form):
        form.instance.user = self.request.user # Assigns the expense to the logged-in user [cite: 18]
        return super().form_valid(form)

# UPDATE VIEW 
class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'skillsswp/expense_form.html'
    success_url = reverse_lazy('expense_list')

# DELETE VIEW
class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'skillsswp/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')