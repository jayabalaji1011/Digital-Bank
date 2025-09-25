from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction as db_transaction
from .models import *
from .forms import *
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io

# ----------- STAFF LOGIN & DASHBOARD -----------

def staff_login(request):
    form = StaffLoginForm()
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            staff = Staff.objects.get(username=username, password=password)
            request.session['staff_id'] = staff.id
            request.session['staff_username'] = staff.username
            return redirect('staff_dashboard')
        except Staff.DoesNotExist:
            messages.error(request, "User not found!")
    return render(request, "staff_login.html", {'form': form, 'show_nav': True})

def logout_staff(request):
    request.session.flush()
    messages.success(request, 'Logged Out Successfully!')
    return redirect('staff_login')

def staff_account(request): 
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, "Please Login!")
        return redirect('staff_login')

    staff = Staff.objects.get(id=staff_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        staff.username = username
        staff.save()
        messages.success(request, "Updated successfully!")
        return redirect('staff_account')

    return render(request, 'staff_account.html', {'staff': staff, 'show_nav': True})

def staff_dashboard(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    query = request.GET.get('q', '').strip()
    if query:
        try:
            customer = Customer.objects.get(account_no=query)
            return redirect('customer_detail', pk=customer.customer_id)
        except Customer.DoesNotExist:
            messages.error(request, "No customer found with that account number.")
            return redirect('staff_dashboard')

    recent_transactions = Transaction.objects.select_related("customer").order_by("-date")[:10]
    return render(
        request,
        "staff_dashboard.html",
        {"transactions": recent_transactions, 'show_nav': True}
    )

# ----------- CREATE CUSTOMER WITH INITIAL DEPOSIT -----------

def create_customer(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            with db_transaction.atomic():
                customer = form.save()

                if customer.bank:
                    # Transaction for customer
                    Transaction.objects.create(
                        customer=customer,
                        transaction_type="DEPOSIT",
                        amount=customer.balance,
                        balance_before=0,
                        balance_after=customer.balance,
                        transfer_account=None
                    )
                    # Bank Transaction
                    BankTransaction.objects.create(
                        bank=customer.bank,
                        customer=customer,
                        transaction_type="DEPOSIT",
                        amount=customer.balance,
                        balance_before=customer.bank.balance,
                        balance_after=customer.bank.balance + customer.balance,
                        transfer_account=None
                    )
                    # Update bank balance
                    customer.bank.balance += customer.balance
                    customer.bank.save()

            messages.success(request, "Customer created successfully")
            return redirect('customer_detail', pk=customer.customer_id)
    else:
        form = CustomerForm()

    return render(request, "create_customer.html", {"form": form, 'show_nav': True})

# ----------- CUSTOMER DETAIL & TRANSACTIONS -----------

def customer_detail(request, pk):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    customer = get_object_or_404(Customer, pk=pk)
    transactions = customer.transactions.all().order_by('-date')

    if request.method == "POST":
        if "transaction_type" in request.POST:
            form = TransactionForm(request.POST)
            if form.is_valid():
                with db_transaction.atomic():
                    transaction_obj = form.save(commit=False)
                    transaction_obj.customer = customer
                    bank = customer.bank
                    transaction_obj.balance_before = customer.balance

                    # ---------- DEPOSIT ----------
                    if transaction_obj.transaction_type == "DEPOSIT":
                        customer.balance += transaction_obj.amount
                        bank.balance += transaction_obj.amount
                        transaction_obj.balance_after = customer.balance
                        transaction_obj.transfer_account = None
                        transaction_obj.save()

                        BankTransaction.objects.create(
                            bank=bank,
                            customer=customer,
                            transaction_type="DEPOSIT",
                            amount=transaction_obj.amount,
                            balance_before=bank.balance - transaction_obj.amount,
                            balance_after=bank.balance,
                            transfer_account=None
                        )

                    # ---------- WITHDRAW ----------
                    elif transaction_obj.transaction_type == "WITHDRAW":
                        if customer.balance < transaction_obj.amount:
                            messages.error(request, "Insufficient Balance")
                            return redirect("customer_detail", pk=pk)

                        customer.balance -= transaction_obj.amount
                        bank.balance -= transaction_obj.amount
                        transaction_obj.balance_after = customer.balance
                        transaction_obj.transfer_account = None
                        transaction_obj.save()

                        BankTransaction.objects.create(
                            bank=bank,
                            customer=customer,
                            transaction_type="WITHDRAW",
                            amount=transaction_obj.amount,
                            balance_before=bank.balance + transaction_obj.amount,
                            balance_after=bank.balance,
                            transfer_account=None
                        )

                    # ---------- TRANSFER ----------
                    elif transaction_obj.transaction_type == "TRANSFER":
                        receiver_acc_no = transaction_obj.transfer_account

                        if not receiver_acc_no:
                            messages.error(request, "Receiver account number is required!")
                            return redirect("customer_detail", pk=pk)

                        try:
                            receiver = Customer.objects.get(account_no=receiver_acc_no.strip())
                        except Customer.DoesNotExist:
                            messages.error(request, "Receiver account not found!")
                            return redirect("customer_detail", pk=pk)

                        if customer.balance < transaction_obj.amount:
                            messages.error(request, "Insufficient Balance")
                            return redirect("customer_detail", pk=pk)

                        # Sender transaction
                        customer.balance -= transaction_obj.amount
                        transaction_obj.balance_after = customer.balance
                        transaction_obj.save()

                        BankTransaction.objects.create(
                            bank=bank,
                            customer=customer,
                            transaction_type="TRANSFER",
                            amount=transaction_obj.amount,
                            balance_before=bank.balance,
                            balance_after=bank.balance - transaction_obj.amount,
                            transfer_account=receiver.account_no
                        )

                        bank.balance -= transaction_obj.amount
                        bank.save()
                        customer.save()

                        # Receiver transaction
                        receiver.balance += transaction_obj.amount
                        Transaction.objects.create(
                            customer=receiver,
                            transaction_type="TRANSFER",
                            amount=transaction_obj.amount,
                            balance_before=receiver.balance - transaction_obj.amount,
                            balance_after=receiver.balance,
                            transfer_account=customer.account_no
                        )

                        BankTransaction.objects.create(
                            bank=receiver.bank,
                            customer=receiver,
                            transaction_type="TRANSFER",
                            amount=transaction_obj.amount,
                            balance_before=receiver.bank.balance,
                            balance_after=receiver.bank.balance + transaction_obj.amount,
                            transfer_account=customer.account_no
                        )

                        receiver.bank.balance += transaction_obj.amount
                        receiver.bank.save()
                        receiver.save()

                    # Final save for sender
                    customer.save()
                    bank.save()

                messages.success(request, "Transaction successful")
                return redirect("customer_detail", pk=pk)

        else:
            # Update customer info
            customer.name = request.POST.get("name")
            customer.address = request.POST.get("address")
            customer.mobile = request.POST.get("mobile")
            password = request.POST.get("password")
            if password and password != "******":
                customer.password = make_password(password)
            customer.save()
            messages.success(request, "Updated successfully")
            return redirect("customer_detail", pk=pk)

    else:
        form = TransactionForm()

    return render(request, "customer_detail.html", {
        "customer": customer,
        "transactions": transactions,
        "form": form,
        "bank": customer.bank,
        "show_nav": True,
    })






def bank_dashboard(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    bank = Bank.objects.first()

    # Recent 10 transactions
    transactions = BankTransaction.objects.all().order_by('-date')[:10]

    # Count of customers for this bank
    customer_count = bank.customer_set.count() if bank else 0

    context = {
        'bank': bank,
        'transactions': transactions,
        'customer_count': customer_count,
        'show_nav':True
    }
    return render(request, 'bank.html', context)


# ----------- CUSTOMER PDF DOWNLOAD -----------

def mask_account_mobile(account_no, mobile):
    masked_acc = f"{'*'*6}{account_no[-4:]}"  # first 6 hidden
    masked_mobile = f"{mobile[:5]}{'*'*5}"     # last 5 hidden
    return masked_acc, masked_mobile

def mask_transfer_account(account_no):
    if account_no and len(account_no) > 4:
        return f"{'*'*6}{account_no[-4:]}"
    return account_no or "-"

def download_transactions_pdf(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    transactions = Transaction.objects.filter(customer=customer).order_by('-date')
    masked_acc, masked_mobile = mask_account_mobile(customer.account_no, customer.mobile)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Transaction Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Name:</b> {customer.name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Account No:</b> {masked_acc}", styles['Normal']))
    elements.append(Paragraph(f"<b>Mobile:</b> {masked_mobile}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [["Date", "Type", "Amount", "Balance Before", "Balance After", "Transfer Account"]]
    for txn in transactions:
        masked_transfer = mask_transfer_account(txn.transfer_account)
        data.append([
            txn.date.strftime("%d-%m-%Y %H:%M"),
            txn.transaction_type,
            f"₹ {txn.amount}",
            f"₹ {txn.balance_before}",
            f"₹ {txn.balance_after}",
            masked_transfer
        ])

    table = Table(data, hAlign="CENTER")
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=transactions_{customer.customer_id}.pdf'
    return response



# ----------- CUSTOMER LOGIN & DASHBOARD -----------

def customer_login(request):
    """Customer login view"""
    form = CustomerLoginForm()
    if request.method == "POST":
        mobile = request.POST['mobile']
        password = request.POST['password']
        try:
            customer = Customer.objects.get(mobile=mobile, password=password)
            request.session['customer_id'] = customer.customer_id
            request.session['customer_name'] = customer.name
            return redirect('customer_dashboard')
        except Customer.DoesNotExist:
            messages.error(request, "User not found!")
    return render(request, "customer_login.html", {'form': form, 'show_navbar': True})


def logout_customer(request):
    request.session.flush()
    messages.success(request, 'Logged Out Successfully!')
    return redirect('customer_login')


def customer_dashboard(request):
    """Customer dashboard after login"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = get_object_or_404(Customer, customer_id=customer_id)
    transactions = Transaction.objects.filter(customer=customer).order_by('-date')

    return render(request, 'customer_dashboard.html', {
        'customer': customer,
        'transactions': transactions,
        'show_navbar': True
    })


def my_transaction(request):
    """View all transactions for customer"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = get_object_or_404(Customer, customer_id=customer_id)
    transactions = Transaction.objects.filter(customer=customer).order_by('-date')

    return render(request,'my_transaction.html',{
        'customer': customer,
        'transactions': transactions,
        'show_navbar': True
    })
