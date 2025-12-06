from rest_framework import permissions,generics,status
from rest_framework.response import Response

from transactions.models import Transaction
from transactions.serializers import Transaction_Serializer


class TransactionApi(generics.GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class =Transaction_Serializer

    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.data.get('action')
        data = request.data.get('data')

        if action == 'create':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            transaction = serializer.save()
            return Response(self.get_serializer(transaction).data, status=status.HTTP_201_CREATED)
        elif action == 'update':
            transaction_id = data.get('id')
            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=data, instance=transaction)
            serializer.is_valid(raise_exception=True)
            transaction = serializer.save()
            return Response(self.get_serializer(transaction).data, status=status.HTTP_200_OK)
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