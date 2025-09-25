from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Staff
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/create_customer/", views.create_customer, name="create_customer"),
    path("staff/customer/<int:pk>/", views.customer_detail, name="customer_detail"),
    path('staff_account/',views.staff_account,name='staff_account'),
    path('bank_dashboard/',views.bank_dashboard,name='bank_dashboard'),
    path('logout_staff/',views.logout_staff,name='logout_staff'),

    # Customer
    path("customer/login/", views.customer_login, name="customer_login"),
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path('logout_customer/',views.logout_customer,name='logout_customer'),
     path('my_transaction/',views.my_transaction,name='my_transaction'),
    path('customer/<int:customer_id>/transactions/pdf/', views.download_transactions_pdf, name='download_transactions_pdf'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
