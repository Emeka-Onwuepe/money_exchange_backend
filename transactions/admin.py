from django.contrib import admin

from transactions.models import Payment, Rate, Transaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Payment)
admin.site.register(Rate)



