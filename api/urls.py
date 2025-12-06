from rest_framework import routers
from django.urls import path
from knox import views as KnoxView

from api.apis.transaction import TransactionApi
from api.apis.users import (CustomerApi, EditUser, 
                            LoginUser,
                             PayeeApi, RegisterUser)

# from api.apis.whatsapp import Whatsapp_Hooks

router = routers.DefaultRouter()

app_name="apis"
 

urlpatterns = [
    # users apis
    path('register', RegisterUser.as_view(), name="register"),
    path('edituser',EditUser.as_view(),name='editUser'),
    path('login', LoginUser.as_view(), name="login"),
    path('logout', KnoxView.LogoutView.as_view(), name="knox_logout"),

    # customer apis
    path('customer', CustomerApi.as_view(), name="customer"),
    # payee apis
    path('payee', PayeeApi.as_view(), name="payee"),
    # transaction apis
    path('transaction', TransactionApi.as_view(), name="transaction"),
    
]

urlpatterns += router.urls
