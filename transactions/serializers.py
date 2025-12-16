from transactions.models import Payment, Transaction
from rest_framework import serializers



class Transaction_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        
class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'