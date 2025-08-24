from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # tailor account
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default="Male")
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Measurement(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    
    bust = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hips = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shoulder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sleeve_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    top_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    trouser_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    neck = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.name}'s Measurements"

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    style_name = models.CharField(max_length=100)
    fabric_type = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    delivery_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} - {self.style_name}"

    def total_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    def balance(self):
        return float(self.price) - float(self.total_paid())

    def payment_status(self):
        if self.total_paid() >= self.price:
            return 'Paid'
        elif self.total_paid() > 0:
            return 'Part-paid'
        else:
            return 'Unpaid'

class Reminder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    remind_at = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.order}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)  # already fixed
    method = models.CharField(
        max_length=50,
        choices=[('cash', 'Cash'), ('transfer', 'Transfer'), ('pos', 'POS')],
        default='cash'
    )
    note = models.TextField(blank=True, null=True)  # <-- match DB column name

    def __str__(self):
        return f"Payment of ₦{self.amount} for {self.order}"
