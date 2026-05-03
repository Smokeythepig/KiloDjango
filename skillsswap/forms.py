from django import forms
from .models import Expense # The dot (.) means "look in the current folder"
from django.core.exceptions import ValidationError
from datetime import date

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        # Fields the user will interact with
        fields = ['date', 'amount', 'category', 'description']
        
        # HTML widget to show a calendar picker
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        # Check if amount is None first to avoid errors if the field is empty
        if amount is not None and amount <= 0:
            raise forms.ValidationError("The amount must be greater than zero.")
        return amount

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date > date.today():
            raise forms.ValidationError("You cannot log an expense for a future date.")
        return selected_date   
