from django.utils import timezone
from django.db import models

from users.models import Customer, Payee

currencies = (
                ("RMB","RMB"),
                ("USD","USD"),
                ("EURO","EURO"),
                ("GBP","GBP"),
                ("YEN","YEN"),
                ("CAD","CAD"),
                ("AUD","AUD"),
                ("CHF","CHF"),
                ("INR","INR"),
                ("PKR","PKR"),
                )

banks = (('none','none'),
         ('access','access'),
         ('gtb','gtb'),
         ('zenith','zenith'),
         ('uba','uba'),
         ('firstbank','firstbank'),
         ('fidelity','fidelity'),
         ('polaris','polaris'),
         ('wema','wema'),
         ('sterling','sterling'),
         ('kuda','kuda'),
         ('opay','opay'),
         ('paycom','paycom'),
         ('ecobank','ecobank'),
         ('fcmb','fcmb'),
         ('providus','providus'),
         ('jaiz','jaiz'),
         ('suntrust','suntrust'),
         ('albaraka','albaraka'),
         ('citibank','citibank'),
         ('standard chartered','standard chartered'),
         )

channels = (('transfer','transfer'),
            ('cash','cash'),
            # ('credit','credit')
            )

class Transaction(models.Model):
    """Model definition for Transaction."""

    # TODO: Define fields here
    date = models.DateField(blank=True)
    transaction_id = models.CharField(max_length=100, unique=True,null=True, blank=True)
    base_currency = models.CharField(max_length=4,
                                      choices = currencies ,default='RMB')
    usd_rate = models.FloatField(default=0.0)
    naira_rate_cp = models.FloatField(default=0.0)
    naira_rate_sp = models.FloatField(default=0.0)
    amount = models.FloatField(default=0.0)
    payee = models.ForeignKey(Payee, related_name='transaction_payee', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='transaction_customer', on_delete=models.CASCADE)
    reciept = models.FileField(upload_to='receipts/', null=True, blank=True)
    # naira = models.FloatField(default=0.0)
    naira_cp = models.FloatField(default=0.0)
    naira_sp = models.FloatField(default=0.0)
    naira_gain = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    channel = models.CharField(max_length=8,
                                      choices = channels ,default='transfer')
    bank = models.CharField(max_length=20,
                                      choices = banks ,default='none')
    paid_once = models.BooleanField(default=True)


    class Meta:
        """Meta definition for Transaction."""

        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-id']


    def __str__(self):
        """Unicode representation of Transaction."""
        return f"{self.customer.full_name} - {self.base_currency} {self.amount}  on {self.date}"
    
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args,**kwargs)

  

class Rate(models.Model):
    """Model definition for Rate."""
    # Your Backup Code is
    # c775 fbd6 de26 866d
    # 941713
    # dan1.host-ww.net
    # backend.divineexservices.com.ng

    # TODO: Define fields here
    currency = models.CharField(max_length=4,
                                      choices = currencies ,default='RMB')
    rate = models.FloatField(default=0.0)
    naira_rate = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for Rate."""

        verbose_name = 'Rate'
        verbose_name_plural = 'Rates'

    def __str__(self):
        """Unicode representation of Rate."""
        return f"{self.currency} {self.rate}  on {self.date}"


class Payment(models.Model):
    """Model definition for Payment."""

    # TODO: Define fields here
    date = models.DateField(blank=True)
    amount = models.FloatField(default=0.0)
    transaction = models.ForeignKey(Transaction, related_name='payment_transaction', on_delete=models.CASCADE)
    channel = models.CharField(max_length=8,
                                      choices = channels ,default='transfer')
    bank = models.CharField(max_length=20,
                                      choices = banks ,default='none')

    class Meta:
        """Meta definition for Payment."""

        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-date']

    def __str__(self):
        """Unicode representation of Payment."""
        return f"{self.transaction.customer.full_name} {self.amount} {self.date}"
    
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args,**kwargs)