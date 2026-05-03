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