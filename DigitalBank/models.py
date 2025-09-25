from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.utils import timezone
import random


class Bank(models.Model):
    name = models.CharField(max_length=200)
    ifsc = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # total bank balance

    def __str__(self):
        return f"{self.name} - {self.branch}"


class Customer(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('SAVINGS', 'Savings'),
        ('CURRENT', 'Current'),
    ]

    customer_id = models.AutoField(primary_key=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15, unique=True)
    aadhar = models.CharField(max_length=12, unique=True)
    dob = models.DateField()
    address = models.TextField(max_length=100)
    account_no = models.CharField(max_length=10, unique=True, editable=False)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    password = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if not self.account_no:
            self.account_no = str(random.randint(1000000000, 9999999999))
        if not self.password:
            dob_str = self.dob.strftime("%d%m%y")
            self.password = self.mobile[-6:] + dob_str
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.account_no}"


class Staff(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('TRANSFER', 'Transfer'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Store "other side" account
    transfer_account = models.CharField(max_length=10, null=True, blank=True)

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.account_no} - {self.transaction_type} {self.amount}"


class BankTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
        ('TRANSFER', 'Transfer'),
    ]

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="bank_transactions")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="bank_transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    transfer_account = models.CharField(max_length=10, null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} by {self.customer.name}"
