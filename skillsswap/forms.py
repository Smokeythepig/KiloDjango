from django import forms #imports django forms module, gives base classes for creating forms
from .models import Expense #imports Expense model from the same directory so the form knows which database table
#it's mapped to
from django.core.exceptions import ValidationError #lets us manually trigger errors if the submitted data 
#doesn't meet criteria
from datetime import date #used to have today's date available
from django.contrib.auth.forms import UserCreationForm #built in-Django form that handles new user registration
from django.contrib.auth.models import User #imports default Django User model


class ExpenseForm(forms.ModelForm):  #is a ModelForm, directs Django to automatically build the form fields based on
    #our Expense database model
    class Meta:  #nested class telling Django which model to use and which fields to display in html
        model = Expense
        # Fields the user will interact with
        fields = ['date', 'amount', 'category', 'description']
        
        # HTML widget to show a calendar picker (otherwise default, Django shows text box for dates, this widgets
        #line allows for html attribute (type='date') to be added
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    #The following methods starting with clean_ are sought out by Django to do specific logic on a field before saving.
    def clean_amount(self):     #Retrieves amount from cleaned_data (data after basic type checking in django)
        amount = self.cleaned_data.get('amount')
        
        if amount is not None and amount <= 0:  # Check if amount is None/negative first to avoid errors if the field is empty
            raise forms.ValidationError("The amount must be greater than zero.")
        return amount

    def clean_date(self):  #Comnpares selected_date to date.today()
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date > date.today():
            raise forms.ValidationError("You cannot log an expense for a future date.")
        return selected_date   

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
