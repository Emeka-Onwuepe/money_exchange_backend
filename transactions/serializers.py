from transactions.models import Payment, Transaction
from rest_framework import serializers



class Transaction_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('amount', 'base_currency', 'channel', 'customer', 
                   'naira_rate', 'payee', 'reciept','usd_price','usd_rate'
                  )
        
class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'