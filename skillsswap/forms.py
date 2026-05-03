from django import forms
from .models import Expense # The dot (.) means "look in the current folder"

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        # Fields the user will interact with
        fields = ['date', 'amount', 'category', 'description']
        
        # HTML widget to show a calendar picker
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

 # Validation 1: Amount must be positive
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("The amount must be greater than zero.")
        return amount

    # Validation 2: Date cannot be in the future
    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date > date.today():
            raise ValidationError("You cannot log an expense for a future date.")
        return selected_date   