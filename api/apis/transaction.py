from rest_framework import permissions,generics,status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from transactions.models import Payment, Transaction
from transactions.serializers import Payment_Serializer, Transaction_Serializer


class TransactionApi(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class =Transaction_Serializer
    parser_classes = (MultiPartParser, FormParser)


    
    def get(self, request, *args, **kwargs):
        transactions = None
        action = request.query_params.get('action', None)
        print("action",action)
        if action == "customer":
            customer_id = request.query_params.get('customer', None)
            transactions = Transaction.objects.filter(customer=int(customer_id))
        elif action == "payee":
            payee_id = request.query_params.get('payee', None)
            transactions = Transaction.objects.filter(payee=int(payee_id))
        elif action == 'date':
            date = request.query_params.get('date', None)
            transactions = Transaction.objects.filter(date=date)
        else:
            transactions = Transaction.objects.all()
        serializer = self.get_serializer(transactions, many=True)
        return Response({"transactions": serializer.data}, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.data.get('action')
        data = request.data
        # del data['action']

        if action == 'create':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            transaction = serializer.save()
            return Response({"transaction":self.get_serializer(transaction).data}, status=status.HTTP_201_CREATED)
        elif action == 'update':
            transaction_id = data.get('id')
            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=data, instance=transaction)
            serializer.is_valid(raise_exception=True)
            transaction = serializer.save()
            return Response({"transaction":self.get_serializer(transaction).data}, status=status.HTTP_201_CREATED)
        elif action == 'delete':
            transaction_id = data.get('id')
            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            transaction.delete()
            return Response({'message': 'Transaction deleted'}, status=status.HTTP_200_OK)
        # Implement transaction logic here based on action
        return Response({'message':'Transaction API not yet implemented'},status=status.HTTP_200_OK)
    




class paymentApi(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class =Payment_Serializer


    def get(self, request, *args, **kwargs):
        transaction_id = request.query_params['transaction_id']
        payments = Payment.objects.filter(transaction=int(transaction_id))
        serializer = self.get_serializer(payments, many=True)
        return Response({"payments": serializer.data}, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.data.get('action')
        data = request.data['data']
        # del data['action']

        if action == 'create':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            return Response({"payment":self.get_serializer(payment).data}, status=status.HTTP_201_CREATED)
        elif action == 'update':
            payment_id = data.get('id')
            try:
                payment = Payment.objects.get(id=payment_id)
            except payment.DoesNotExist:
                return Response({'error': 'payment not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=data, instance=payment)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            return Response({"payment":self.get_serializer(payment).data}, status=status.HTTP_201_CREATED)
        elif action == 'delete':
            payment_id = data.get('id')
            try:
                payment = Payment.objects.get(id=payment_id)
            except payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
            payment.delete()
            return Response({'message': 'Payment deleted'}, status=status.HTTP_200_OK)
        # Implement payment logic here based on action
        return Response({'message':'Payment API not yet implemented'},status=status.HTTP_200_OK)