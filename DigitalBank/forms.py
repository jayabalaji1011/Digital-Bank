from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *

from django import forms
from .models import Customer, Transaction


class StaffLoginForm(forms.Form):
    username = forms.CharField(max_length=15, 
    label="Username",
    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'})                         )
    password = forms.CharField(
    label='Password',        
    widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'})
    )


class CustomerLoginForm(forms.Form):
    mobile = forms.CharField(
        label="Mobile Number",
        max_length=10,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mobile Number'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'})
    )




class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['bank', 'name', 'mobile', 'aadhar', 'dob', 'address', 'account_type', 'balance']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhar': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  
                'style': 'resize:none;'  
            }),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control',}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = Customer
        # Don't include account_no or password in form
        fields = ['bank', 'name', 'mobile', 'aadhar', 'dob', 'address', 'account_type', 'balance']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhar': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
        }




class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'transfer_account']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'transfer_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Receiver Account No'
            }),
        }

