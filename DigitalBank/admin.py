from django.contrib import admin
from .models import *

# Staff Admin
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('username',)
    search_fields = ('username',)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "branch", "ifsc", "state", "balance")
    search_fields = ("name", "ifsc", "branch")
    list_filter = ("state",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "account_no", "mobile", "balance", "account_type", "bank")
    search_fields = ("name", "mobile", "account_no")
    list_filter = ("account_type", "bank")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("customer", "transaction_type", "transfer_account", "amount", "balance_before", "balance_after", "date")
    search_fields = ("customer__name", "customer__account_no")
    list_filter = ("transaction_type", "date")


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ("bank", "customer", "transaction_type", "transfer_account", "amount", "balance_before", "balance_after", "date")
    search_fields = ("bank__name", "customer__name", "customer__account_no")
    list_filter = ("transaction_type", "date", "bank")
