from django.db import models
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