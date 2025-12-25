from users.models import Customer, Payee
from users.serializers import (Customer_Serializer, Edit_Customer_Serializer, Get_User_Serializer, Payee_Serializer,User_Serializer, 
                               Login_Serializer,Edit_User_Serializer)
from django.contrib.auth import get_user_model
User=get_user_model()
from rest_framework import permissions,generics,status
from rest_framework.response import Response
from knox.models import AuthToken
# from rest_framework.parsers import MultiPartParser, FormParser



class LoginUser(generics.GenericAPIView):
    serializer_class = Login_Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)
        returnedUser = Get_User_Serializer(user)
        return Response({"user": returnedUser.data, "token": token})

class RegisterUser(generics.GenericAPIView):
    serializer_class = User_Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _,token=AuthToken.objects.create(user)
        returnedUser=Get_User_Serializer(user)
        return Response({"user":returnedUser.data,
                         "token":token
                         })

        
class EditUser(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = Edit_User_Serializer
    # parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user = request.user 
        
        serializer = self.get_serializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        returnedUser = Get_User_Serializer(user)
        return Response({"user": returnedUser.data, "token": token})
        return Response({'message':'An error occurred'},status=status.HTTP_400_BAD_REQUEST)
    

class CustomerApi(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class =Customer_Serializer

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        serializer = self.get_serializer(customers, many=True)
        return Response({"customers": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.data.get('action')
        data = request.data.get('data')

        if action == 'create':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            customer = serializer.save()
            return Response({"customer":self.get_serializer(customer).data})
      
        elif action == 'update':
            customer_id = data.get('id')
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = Edit_Customer_Serializer(data=data, instance=customer)
            serializer.is_valid(raise_exception=True)
            customer = serializer.save()
            return Response({"customer":self.get_serializer(customer).data})
        elif action == 'delete':
            customer_id = data.get('id')
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            customer.delete()
            return Response({'message': 'Customer deleted'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


class PayeeApi(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class =Payee_Serializer

    def get(self, request, *args, **kwargs):
        payees = Payee.objects.all()
        serializer = self.get_serializer(payees, many=True)
        print(serializer.data)
        return Response({"payees": serializer.data})


    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.data.get('action')
        data = request.data.get('data')

        if action == 'create':
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            payee = serializer.save()
            return Response({"payee":self.get_serializer(payee).data})
        
        elif action == 'update':
            payee_id = data.get('id')
            try:
                payee = Payee.objects.get(id=payee_id)
            except Payee.DoesNotExist:
                return Response({'error': 'Payee not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=data, instance=payee)
            serializer.is_valid(raise_exception=True)
            payee = serializer.save()
            return Response({"payee":self.get_serializer(payee).data})
        elif action == 'delete':
            payee_id = data.get('id')
            try:
                payee = Payee.objects.get(id=payee_id)
            except Payee.DoesNotExist:
                return Response({'error': 'Payee not found'}, status=status.HTTP_404_NOT_FOUND)
            payee.delete()
            return Response({'message': 'Payee deleted'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
