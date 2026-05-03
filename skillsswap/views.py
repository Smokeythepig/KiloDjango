from django.shortcuts import render
from .models import Skill

def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skillsswap/skill_list.html', {'skills': skills})

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Expense
from .forms import ExpenseForm

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