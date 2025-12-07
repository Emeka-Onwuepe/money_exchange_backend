from django.db.models.signals import (post_save,post_delete,
                                      pre_delete,pre_save)
from django.dispatch import receiver
from django.db import models
from transactions.models import Payment, Transaction
from users.models import Customer

#  date = models.DateField(auto_now_add=True)
    # transaction_id = models.CharField(max_length=100, unique=True)
    # base_currency = models.CharField(max_length=4,
    #                                   choices = currencies ,default='RMB')
    # usd_rate = models.FloatField(default=0.0)
    # usd_price = models.FloatField(default=0.0)
    # naira_rate = models.FloatField(default=0.0)
    # amount = models.FloatField(default=0.0)
    # payee = models.ForeignKey(Payee, related_name='transaction_payee', on_delete=models.CASCADE)
    # customer = models.ForeignKey(Customer, related_name='transaction_customer', on_delete=models.CASCADE)
    # reciept = models.FileField(upload_to='receipts/', null=True, blank=True)
    # naira = models.FloatField(default=0.0)
    # usd_bid = models.FloatField(default=0.0)
    # usd_ask = models.FloatField(default=0.0)
    # usd_gain = models.FloatField(default=0.0)
    # balance = models.FloatField(default=0.0)
    # paid_amount = models.FloatField(default=0.0)
    # channel = models.CharField(max_length=8,
    #                                   choices = channels ,default='transfer')
    # paid_once = models.BooleanField(default=True)

    # <td>{(exchange.amount / exchange.usd_rate).toFixed(1)}</td>
    #                 <td>{.toFixed(1)}</td>
    #                 <td>{toFixed(1)}</td>
    #                 <td>{}</td>
    #                 

@receiver(pre_save, sender=Transaction)
def create_transaction(sender, instance, **kwargs):
    customer = None
    old = None
    try:
        customer = Customer.objects.get(pk=instance.customer.id)
    except Customer.DoesNotExist:
        return
    
    if instance.pk:
        old = Transaction.objects.get(pk = instance.pk)


    instance.naira = round((instance.amount * instance.naira_rate),2)     
    instance.usd_ask = round((instance.amount / instance.usd_rate),2)
    instance.usd_bid = round((instance.amount / instance.usd_price),2)
    instance.usd_gain = round((((1/instance.usd_price) - (1/instance.usd_rate)) * instance.amount),2)


    if not instance.pk:
        transaction_id = "kjkjkjk"  # Replace with actual logic to generate transaction ID
        instance.transaction_id = transaction_id
        balance = round((instance.paid_amount - instance.naira),2)
        instance.balance = balance
        customer.balance += balance
        customer.save()
    elif instance.pk:
        # check if naira or paid_amount changed
        if (old.paid_amount != instance.paid_amount) or (old.naira != instance.naira):
            total_payments = Payment.objects.filter(transaction=instance).aggregate(total=models.Sum('amount'))['total'] or 0.0
            # print("old", old.paid_amount)
            # print("new",instance.paid_amount)
            # print("BALANCE",instance.balance)
            instance.balance = round((instance.paid_amount - instance.naira) + total_payments,2)
            # print("updated",instance.balance)

        # check if the balance was edited
        if old.balance != instance.balance:
            # balance edited
            diff = instance.balance - old.balance
            # print("diff",diff)
            customer.balance += diff
            customer.save()

    if instance.balance < 0 and not instance.pk:
        instance.paid_once = False

        

@receiver(pre_delete, sender=Transaction)
def delete_transaction(sender, instance, **kwargs):
    customer = None
    try:
        customer = Customer.objects.get(pk=instance.customer.id)
    except Customer.DoesNotExist:
        return
    
    total_payments = Payment.objects.filter(transaction=instance).aggregate(total=models.Sum('amount'))['total'] or 0.0
    customer.balance -= instance.balance + total_payments
    customer.save()


@receiver(pre_save, sender=Payment)
def create_payment(sender,instance,**kwargs):
    transaction = Transaction.objects.get(pk = instance.transaction.id)

    if instance.pk:
        old = Payment.objects.get(pk = instance.pk)

        if old.amount != instance.amount:
            diff = instance.amount - old.amount
            transaction.balance += diff
            transaction.save()
    else:
        transaction.balance += instance.amount
        transaction.save()

@receiver(post_delete, sender=Payment)
def delete_payment(sender, instance, **kwargs):
    transaction = None
    try:
        transaction = Transaction.objects.get(pk=instance.transaction.id)
        print("transaction found")
    except Transaction.DoesNotExist:
        return

    transaction.balance += instance.amount
    transaction.save()

