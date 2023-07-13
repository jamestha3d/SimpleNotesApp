from django.db import models
from accounts.models import User
# Create your models here.

class StripeCustomer(User):
    stripe_customer_id = models.CharField(max_length=100, blank=False, null=True, default=None)
    
