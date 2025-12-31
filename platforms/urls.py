from django.contrib import admin
from django.urls import path,include

from platforms.views import Whatsapp_Hooks, get_abs, get_media_file,send_whatsapp_message

app_name="platform"
urlpatterns = [
    path('hooks123',Whatsapp_Hooks,name='hooks'),
    # path('send/<str:message>',send_whatsapp_message,name='send_message'),
    # path('get_media/<str:media_id>',get_media_file,name='get_media'),
    # path('get_abs',get_abs,name='get_abs')
    
    ] 