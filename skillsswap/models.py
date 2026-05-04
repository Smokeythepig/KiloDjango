from django.db import models #without it, just writing classes with no connection to a database
from django.contrib.auth.models import User


class Skill(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    description = models.TextField()

    CATEGORY_CHOICES = [
        ('tutoring', 'Tutoring'),
        ('tech', 'Tech Help'),
        ('design', 'Design'),
        ('fitness', 'Fitness'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    contact_method = models.CharField(
        max_length=50,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('dm', 'Direct Message'),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



from django.contrib.auth.models import User # Required for User Accounts 
#Django comes with built in user system, use it to link skills/expenses to specific users

class Expense(models.Model): #by passing models.Model into class, using inheritance. Now can save data to database, etc.

    user = models.ForeignKey(User, on_delete=models.CASCADE) #logic to create relationships between diff. database tables (ex. entry to a user)
    #above line links expenses to a user (how M:N is managed in database)
    #ForeignKey tells django to not store simple variable but provide path to another table of data (ex.users, line 40)
    #on_delete=models.CASCADE= determines what happens to an an expense if the creator (user) deletes acct,
    #will automatically delete every expense tied to a deleted user account

    
    # Required fields from Checkpoint 3 requirements 
    date = models.DateField() #stores the calendar date
    amount = models.DecimalField(max_digits=10, decimal_places=2)  #use decimal field for mone
    #bc float can lead to rounding errors, max digits for reasonable amount to be entered
    category = models.CharField(max_length=100) 
    description = models.TextField(blank=True) #blank=True means user can leave desc. blank without raising an error
    
    # Track when records are created/updated 
    created_at = models.DateTimeField(auto_now_add=True)
    #above collects exact date and time object is first created and saved, doesn't change once set.
    updated_at = models.DateTimeField(auto_now=True)  #unlike auto_now_add, auto_now updates every
    #single time user hits save; helps track when an entry was last edited. 
    #usually for auditing purposes/integrity, sorting

    def __str__(self): #magic method, controls how the object appears in Django Admin panel/dropdowns.
        #if not used, django would simply show something like "Expense object(1)"
        #returns natural language string for easy viewing from developer's end
        return f"{self.date} - {self.category}: ${self.amount}"
