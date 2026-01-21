from django.http import FileResponse
from rest_framework import permissions,generics,status
from rest_framework.response import Response
from django.db import models
from datetime import date
from transactions.models import Payment, Transaction
from transactions.serializers import (Income_Serializer,TransactionDepth_Serializer)
import pandas as pd
import numpy as np
import os

class AnalyticsApi(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        data = request.data['data']

        action_group =['get_statement', 'download_statement','get_today_statement',
                       ]

        if action in action_group:
            start_date = data.get('start')
            end_date = data.get('end')
            # if action == 'get_today_statement':
            #     start_date = date.today()
            #     end_date = date.today()
            transactions = Transaction.objects.filter(date__range=[start_date, end_date])
            payments = Payment.objects.filter(date__range=[start_date, end_date])


            agg = transactions.aggregate(
                # total_amount=models.Sum('amount'),
                total_naira_cp=models.Sum('naira_cp'),
                total_naira_sp=models.Sum('naira_sp'),
                total_naira_gain=models.Sum('naira_gain'),
                total_payments_in_naira = models.Sum('balance') + models.Sum('naira_sp') ,
                total_balance_in_naria=models.Sum('balance'),

            )
            grouped_agg = transactions.values('base_currency').annotate(
                total_amount=models.Sum('amount'),
                total_naira_cp=models.Sum('naira_cp'),
                total_naira_sp=models.Sum('naira_sp'),
                total_naira_gain=models.Sum('naira_gain'),
                # total_naira=models.Sum('naira'),
                total_payments_in_naira = models.Sum('balance') + models.Sum('naira_sp') ,
                total_balance_in_naria=models.Sum('balance'),

            )

            transactions_income = transactions.filter(paid_amount__gt=0).annotate(
                full_name=models.F('customer__full_name'),
                payee_name=models.F('payee__name'),
                transactionId=models.F('transaction_id'),
                transaction_amount = models.F('amount'),
                nature=models.Value('Transaction', output_field=models.CharField()),
            ).values('date', 'paid_amount', 'channel','bank' ,'full_name', 'transactionId',
                     'base_currency','transaction_amount', 'payee_name', 'nature')



            payments_income = payments.annotate(
                full_name=models.F('transaction__customer__full_name'),
                paid_amount=models.F('amount'),
                payee_name=models.F('transaction__payee__name'),
                transactionId=models.F('transaction__transaction_id'),
                base_currency = models.F('transaction__base_currency'),

                transaction_amount = models.F('transaction__amount'),
                nature=models.Value('Payment', output_field=models.CharField()),

            ).values('date','paid_amount', 'full_name', 'channel', 'bank',
                    'transactionId','base_currency','transaction_amount',
                    'payee_name', 'nature')

            incomes = list(transactions_income) + list(payments_income)

            # sort by date
            incomes.sort(key=lambda x: x['date'])
            total_income = sum(item.get('paid_amount', 0) for item in incomes)
            total_income_by_chaennel = {}
            total_income_by_bank = {}
            for item in incomes:
                channel = item.get('channel')
                bank = item.get('bank')
                amount = item.get('paid_amount', 0) 
                total_income_by_chaennel[channel] = total_income_by_chaennel.get(channel, 0) + amount
                total_income_by_bank[bank] = total_income_by_bank.get(bank, 0) + amount
            if 'none' in total_income_by_bank:
                del total_income_by_bank['none']
            total_income_by_bank['total_amount'] = sum(total_income_by_bank.values())

            statement_data = {
                    "overall": agg,
                    "by_currency": list(grouped_agg),
                    'transactions': TransactionDepth_Serializer(transactions, many=True).data,
                    # 'payments': PaymentDepth_Serializer(payments, many=True).data,
                    'incomes': Income_Serializer(incomes, many=True).data,
                    'total_income': total_income,
                    'total_income_by_channel': total_income_by_chaennel,
                    'total_income_by_bank': total_income_by_bank,
                }
            
            # for transaction in transactions:
            if action != 'download_statement':
                return Response({ 'analysis': statement_data}, status=status.HTTP_200_OK)
            elif action == 'download_statement':
                # Generate CSV files for transactions and payments
                transactions_df = pd.DataFrame(statement_data['transactions'])
                if len(statement_data['transactions'])>0:
                    transactions_df['payee'] = transactions_df['payee'].apply(lambda x: x['name'] if isinstance(x, dict) else x)
                    transactions_df['customer'] = transactions_df['customer'].apply(lambda x: x['full_name'] if isinstance(x, dict) else x)
                    transactions_df.drop(columns=['reciept'], inplace=True)
                # payments_df = pd.DataFrame(statement_data['payments'])
                incomes_df = pd.DataFrame(statement_data['incomes'])
                overall_df = pd.DataFrame([statement_data['overall']])
                by_currency_df = pd.DataFrame(statement_data['by_currency'])
                total_income_df = pd.DataFrame([{'Total Income': statement_data['total_income']}])
                total_income_by_channel_df = pd.DataFrame(list(statement_data['total_income_by_channel'].items()),
                                                           columns=['Channel', 'Total'])
                total_income_by_bank_df = pd.DataFrame(list(statement_data['total_income_by_bank'].items()),
                                                           columns=['Bank', 'Total'])

                folder_path = 'media/statements/'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                workbook_name = 'statement.xlsx'
                worksheet_path = f'{folder_path}{workbook_name}'
                work_sheet_url = request.build_absolute_uri(f'/{worksheet_path}')
                start_row = 0

                with pd.ExcelWriter(worksheet_path, engine='xlsxwriter') as writer:
                    transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
                    # payments_df.to_excel(writer, sheet_name='Payments', index=False)
                    incomes_df.to_excel(writer, sheet_name='Incomes', index=False)
                    start_row = len(incomes_df) + 3
                    total_income_by_bank_df.to_excel(writer, sheet_name='Incomes',
                                                        startrow=start_row, index=False)
                    start_row += len(total_income_by_bank_df) + 3
                    total_income_by_channel_df.to_excel(writer, sheet_name='Incomes', 
                                                        startrow=start_row, index=False)
                    start_row += len(total_income_by_channel_df) + 3
                    total_income_df.to_excel(writer, sheet_name='Incomes',
                                              startrow=start_row, index=False)

                    
                    overall_df.to_excel(writer, sheet_name='Overall Summary', index=False)
                    by_currency_df.to_excel(writer, sheet_name='Overall Summary', startrow=len(overall_df)+4, index=False)
                    
                    for sheet_name in writer.sheets:
                        writer.sheets[sheet_name].autofit()



                return Response({'statement_url': work_sheet_url}, status=status.HTTP_200_OK)


        # Placeholder for analytics processing logic
        return Response({"message": "Analytics data processed"}, status=status.HTTP_200_OK)             