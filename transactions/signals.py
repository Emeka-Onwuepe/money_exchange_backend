from django.db.models.signals import (post_save,post_delete,
                                      pre_delete,pre_save)
from django.dispatch import receiver
from django.db import models
from transactions.helper import generate_id
from transactions.models import Payment, Transaction
from users.models import Customer              

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


    instance.naira_sp = round((instance.amount * instance.naira_rate_sp),2)
    instance.naira_cp = round((instance.amount * instance.naira_rate_cp),2)
    instance.naira_gain = round((instance.naira_sp - instance.naira_cp),2) 


    if not instance.pk:
        transaction_id = generate_id(instance.base_currency) 
        instance.transaction_id = transaction_id
        balance = round((instance.paid_amount - instance.naira_sp),2)
        instance.balance = balance
        customer.balance += balance
        customer.save()
    elif instance.pk:
        # check if naira or paid_amount changed
        if (old.paid_amount != instance.paid_amount) or (old.naira_sp != instance.naira_sp):
            total_payments = Payment.objects.filter(transaction=instance).aggregate(total=models.Sum('amount'))['total'] or 0.0
            # print("old", old.paid_amount)
            # print("new",instance.paid_amount)
            # print("BALANCE",instance.balance)
            instance.balance = round((instance.paid_amount - instance.naira_sp) + total_payments,2)
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

