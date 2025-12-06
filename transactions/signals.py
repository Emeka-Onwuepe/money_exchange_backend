from django.db.models.signals import (post_save,post_delete,
                                      pre_delete,pre_save)
from django.dispatch import receiver
from transactions.models import Transaction
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
    try:
        customer = Customer.objects.get(pk=instance.customer.id)
    except Customer.DoesNotExist:
        return
    
    naira = round((instance.amount * instance.naira_rate),2)
    balance = round((instance.paid_amount - naira),2)
    instance.balance = balance
    print("PAID AMOUNT:", instance.paid_amount)
    print("NAIRA AMOUNT:", naira)
    print("BALANCE BEFORE SAVE SIGNAL:", balance)


    if balance < 0:
        instance.paid_once = False


    if not instance.pk:
        transaction_id = "kjkjkjk"  # Replace with actual logic to generate transaction ID
        instance.transaction_id = transaction_id
        
    instance.naira = naira
    instance.usd_ask = round((instance.amount / instance.usd_rate),2)
    instance.usd_bid = round((instance.amount / instance.usd_price),2)
    instance.usd_gain = round((((1/instance.usd_price) - (1/instance.usd_rate)) * instance.amount),2)

    if instance.pk:
        old = Transaction.objects.get(pk = instance.pk)
        customer.balance -= old.balance
        customer.balance += balance
        customer.save()
    else:
        customer.balance += balance
        customer.save()

    # instance.save()

@receiver(post_delete, sender=Transaction)
def delete_transaction(sender, instance, **kwargs):
    customer = None
    try:
        customer = Customer.objects.get(pk=instance.customer.id)
    except Customer.DoesNotExist:
        return
    
    customer.balance -= instance.balance
    customer.save()