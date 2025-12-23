from rest_framework import permissions,generics,status
from rest_framework.response import Response
from django.db import models

from transactions.models import Payment, Transaction
from transactions.serializers import (Transaction_Serializer,
            PaymentDepth_Serializer,Payment_Serializer, TransactionDepth_Serializer)

class AnalyticsApi(generics.GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        data = request.data['data']

        if action == 'get_statement':
            start_date = data.get('start')
            end_date = data.get('end')
            transactions = Transaction.objects.filter(date__range=[start_date, end_date])
            payments = Payment.objects.filter(date__range=[start_date, end_date])


            agg = transactions.aggregate(
                # total_amount=models.Sum('amount'),
                total_usd_price=models.Sum('usd_price'),
                total_usd_gain=models.Sum('usd_gain'),
                total_usd_rate=models.Sum('usd_rate'),
                total_balance=models.Sum('balance'),
                total_naira=models.Sum('naira')
            )
            grouped_agg = transactions.values('base_currency').annotate(
                total_amount=models.Sum('amount'),
                total_usd_price=models.Sum('usd_price'),
                total_usd_gain=models.Sum('usd_gain'),
                total_usd_rate=models.Sum('usd_rate'),
                total_balance=models.Sum('balance'),
                total_naira=models.Sum('naira')
            )

            payments_agg = payments.values('channel').annotate(
                total_amount=models.Sum('amount'),
            )

            transactions_income = transactions.filter(paid_amount__gt=0).annotate(
                full_name=models.F('customer__full_name'),
                payee_name=models.F('payee__name'),
                transactionId=models.F('transaction_id'),
            ).values('date', 'paid_amount', 'channel', 'full_name', 'transactionId', 'payee_name')



            payments_income = payments.annotate(
                full_name=models.F('transaction__customer__full_name'),
                paid_amount=models.F('amount'),
                payee_name=models.F('transaction__payee__name'),
                transactionId=models.F('transaction__transaction_id'),

            ).values('date','paid_amount', 'full_name', 'channel',
                                              'transactionId','payee_name')

            print("transactions income", transactions_income)
            print("payments income", payments_income)


            incomes = list(transactions_income) + list(payments_income)
            # sort by date
            incomes.sort(key=lambda x: x['date'])
            total_income = sum(item.get('paid_amount', 0) for item in incomes)
            total_income_by_chaennel = {}
            for item in incomes:
                channel = item.get('channel')
                amount = item.get('paid_amount', 0) 
                total_income_by_chaennel[channel] = total_income_by_chaennel.get(channel, 0) + amount
            
            print("total income", total_income)



            
            # for transaction in transactions:


            return Response({ 'analysis': {
                "overall": agg,
                "by_currency": list(grouped_agg),
                'transactions': TransactionDepth_Serializer(transactions, many=True).data,
                'payments': PaymentDepth_Serializer(payments, many=True).data,
                'incomes': incomes,
                'total_income': total_income,
                'total_income_by_channel': total_income_by_chaennel,
            }}, status=status.HTTP_200_OK)
        # Placeholder for analytics processing logic
        return Response({"message": "Analytics data processed"}, status=status.HTTP_200_OK)
