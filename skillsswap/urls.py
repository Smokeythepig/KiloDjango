from django.urls import path #imports the function that connects a URL string to a class or function
from . import views #imports views.py file so the URLs can direct to the logic in that file
from .views import ExpenseListView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView 
#imports pre-built django structures that allow creating, deleting, listing records w less code required
#called class-based views

urlpatterns = [
    path('', views.home, name='home'), #homepage, empty string means it loads when the user visits the site
    path('expenses/', ExpenseListView.as_view(), name='expense_list'),  #links to existing expenses table
    path('add/', ExpenseCreateView.as_view(), name='expense_add'), #links to where you can add expense
    path('edit/<int:pk>/', ExpenseUpdateView.as_view(), name='expense_edit'), #links to how to update existing expenses
    path('delete/<int:pk>/', ExpenseDeleteView.as_view(), name='expense_delete'), #links to where to delete expense
    path('dashboard/', views.dashboard, name='dashboard'), #links to dashboard view
    path('currency/', views.currency_conversion, name='currency_conversion'), #links to currency conversion tool
    path('import/', views.import_expenses, name='import_expenses'), #links to logic handling uploading expense data
    path('register/', views.register, name='register'), #links to user signup page
]
#each points to functions in views.py file
