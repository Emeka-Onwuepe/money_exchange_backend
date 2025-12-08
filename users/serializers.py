from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.models import Customer, Payee
User=get_user_model()
from django.contrib.auth import authenticate

class Get_User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude=["password","last_login","is_active","is_admin","staff",
                    "is_superuser","groups","user_permissions"]

class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email","phone_number",
                  'user_type',"password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data["phone_number"],validated_data["full_name"],
                                        validated_data["user_type"],
                                        validated_data["email"],
                                        password=validated_data["password"]
                                        )
        user.save()
        return user      
    
    
class Edit_User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name','phone_number','email']


class Login_Serializer(serializers.Serializer):
    phone_number= serializers.CharField()
    password= serializers.CharField()
    
    def validate(self,data):
        user= authenticate(**data)
        
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid Credentials")  
    
    
class Customer_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class Edit_Customer_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ("balance",)

class Payee_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Payee
        fields = '__all__'