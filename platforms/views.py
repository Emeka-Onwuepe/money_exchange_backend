import json
from django.db import IntegrityError
import requests
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from platforms.helpers import get_message, send_whatsapp_message_func
from transactions.models import Rate, Transaction
from transactions.serializers import Transaction_Serializer
from users.models import  Customer, Payee, User
from variables import token, phone_id,VERIFY_TOKEN
from django.utils import timezone



# Create your views here.
@csrf_exempt 
def Whatsapp_Hooks(request, *args, **kwargs):

    if request.method == 'GET':
        mode = request.GET['hub.mode']
        challenge = request.GET['hub.challenge']
        verify_token = request.GET['hub.verify_token']
       
        if mode == 'subscribe' and verify_token == VERIFY_TOKEN:
            return HttpResponse(challenge,status=200)
        

    if request.method == 'POST':
        session_minutes = 10
        
        print('message recieved')
        data = json.loads(request.body.decode('utf-8'))
        try:
            if data['entry'][0]['changes'][0]['value'].get('contacts'):

                whatsapp_message = get_message(data)
                print('actionvmmmm',len(whatsapp_message['action']))

                if (timezone.now() - whatsapp_message['timestamp']) > timezone.timedelta(minutes=session_minutes):
                    print('session expired')

                    # remember to decide what to do with the message
                    return HttpResponse({'status':"ok"}, status=200)
                local = f"0{whatsapp_message['sender'][3:]}"
                sender = f"+{whatsapp_message['sender']}"
                user = User.objects.get(phone_number = local)
                if not user.verified:
                    print('not verified')
                    msg = 'You are not authorized to send messages to this number'
                    send_whatsapp_message_func(msg,sender)
                    return HttpResponse({'status':"ok"}, status=200)
                action = whatsapp_message['action'].strip()
                if action == 'add_transaction':
                    data = whatsapp_message['content']
                    customer_name = data['customer'].lower()
                    payee_name = data['payee'].lower()
                    customer = Customer.objects.get(full_name = customer_name)
                    payee = Payee.objects.get(name = payee_name )
                    data['customer'] = customer
                    data['payee'] = payee
                    transaction = Transaction.objects.create(**data)
                    transaction.save()
                    data = Transaction_Serializer(transaction).data
                    msg = 'Transaction added successfully\n'
                    for key,value in data.items():
                        print(key,value)
                        if key not in ['customer','payee',
                                       'id','date','reciept','paid_once']:
                            msg += f"{key} : {value}\n"

                    send_whatsapp_message_func(msg,sender)

                    return HttpResponse({'status':"ok"}, status=200)
                if action == 'set_rate' or action == 'send_rate':
                    did = 'set'
                    data = whatsapp_message['content']
                    for key,value in data.items():
                        rate,created = Rate.objects.get_or_create(currency =key)
                        rate.rate = float(value.strip().replace(',',''))
                        rate.save()
                        if action == 'send_rate':
                            did = 'sent'
                            customers = Customer.objects.all().values_list('phone_number',flat=True)
                            for customer in customers:
                                number = f"+234{customer[1:]}"
                                msg = f"{key} new rate is {value}"
                                res = send_whatsapp_message_func(msg,number)
                    msg = f'Rate {did} successfully'
                    send_whatsapp_message_func(msg,sender)

                    return HttpResponse({'status':"ok"}, status=200)

                       
        except User.DoesNotExist:
            msg = 'You are not authorized to send messages to this number'
            send_whatsapp_message_func(msg,sender)
            return HttpResponse({'status':"ok"}, status=200)
        except IntegrityError:
            return HttpResponse({'status':"ok"}, status=200)
        except Customer.DoesNotExist:
            msg = 'customer not found'
            send_whatsapp_message_func(msg,sender)
            return HttpResponse({'status':"ok"}, status=200)
        except Payee.DoesNotExist:
            msg = 'Payee not found'
            send_whatsapp_message_func(msg,sender)
            return HttpResponse({'status':"ok"}, status=200)
        
        return HttpResponse({'status':"ok"}, status=200)

    return HttpResponse({'status':"ok"}, status=200)



def send_whatsapp_message(request,message):
    send_whatsapp_message_func(message,'+2348132180216')
    # print(request.__dict__)
    
    # response = send_whatsapp_message_func(message)
    # print('hello')
    # url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    # headers = {
    #     "Authorization": f"Bearer {token}",
    #     "Content-Type": "application/json"
    # }
    # payload = {
    #     "messaging_product": "whatsapp",
    #     "to": '+2348132180216',
    #     "type": "text",
    #     "text": {
    #         "body": message
    #     }
    # }
    # response = requests.post(url, headers=headers, json=payload)
    return HttpResponse("hello my guy", status=200)


def get_media_file(request,media_id):
    image_endpoint = url = f"https://graph.facebook.com/v22.0/{media_id}"
    headers = {
        'Authorization': f'Bearer {token}'
        }
    get_image_url = requests.request("GET", image_endpoint, headers=headers, data={})
    if get_image_url.status_code != 200:
        return HttpResponse("Failed to retrieve media url", status=get_image_url.status_code)
    url = get_image_url.json()['url']

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # print(response.content)
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    else:
        return HttpResponse("Failed to retrieve media file", status=response.status_code)
    
def get_abs(request):
    
    # print(allowed_hosts)
    record = Whatsapp_Record.objects.first()
    return HttpResponse(record.get_absolute_url(), status=200)

def facebook_privacy_policy_callback(request):
    """
    This is a placeholder view for the Facebook privacy policy callback.
    It can be used to handle any specific logic related to the callback.
    """

    # You can add any logic you need here, such as logging or redirecting.
    return HttpResponse("Facebook Privacy Policy Callback Received", status=200)


import base64
import hashlib
import hmac
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def facebook_data_deletion_callback(request):
    if request.method == 'POST':
        signed_request = request.POST.get('signed_request')
        data = parse_signed_request(signed_request)
        if not data:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        user_id = data.get('user_id')

        # Start data deletion
        status_url = 'https://www.<your_website>.com/deletion?id=abc123'
        confirmation_code = 'abc123'

        response_data = {
            'url': status_url,
            'confirmation_code': confirmation_code
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def parse_signed_request(signed_request):
    try:
        encoded_sig, payload = signed_request.split('.', 1)
        secret = b'appsecret'  # Use your app secret here

        sig = base64_url_decode(encoded_sig)
        data = json.loads(base64_url_decode(payload))

        expected_sig = hmac.new(secret, payload.encode(), hashlib.sha256).digest()
        if sig != expected_sig:
            # Bad signature
            return None
        return data
    except Exception:
        return None

def base64_url_decode(input_str):
    input_str += '=' * (-len(input_str) % 4)  # Pad with '='
    return base64.urlsafe_b64decode(input_str)