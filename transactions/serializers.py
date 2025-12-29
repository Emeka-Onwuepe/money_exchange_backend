from transactions.models import Payment, Transaction
from rest_framework import serializers



class Transaction_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionDepth_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        depth = 1
        
class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentDepth_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        depth = 2
        fields = '__all__'

class Income_Serializer(serializers.Serializer):
    date = serializers.DateField()
    paid_amount = serializers.FloatField()
    channel = serializers.CharField()
    full_name = serializers.CharField()
    transactionId = serializers.CharField()
    base_currency = serializers.CharField()
    transaction_amount = serializers.FloatField()
    payee_name = serializers.CharField()
    nature = serializers.CharField()  # 'Transaction' or 'Payment'

