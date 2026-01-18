import requests
from datetime import datetime

from variables import phone_id, token


def send_whatsapp_message_func(message,sender):
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": sender,
        "type": "text",
        "text": {
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response

def add_comma(number):
    number_str = str(number).split('.')[0]
    decimal_str = None
    if '.' in str(number):
        decimal_str = str(number).split('.')[1]
    if len(number_str) <= 3:
        if decimal_str:
            return number_str + '.' + decimal_str
        return number_str
    reversed_str = number_str[::-1]
    comma_added_str = ",".join([reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)])
    comma_added_str = comma_added_str[::-1]
    if decimal_str:
        comma_added_str += '.' + decimal_str
    return comma_added_str


def send_rate_template_message(reciever,base,rate):
    rate = float(rate.strip().replace(',',''))
    base = base.upper()
    rate_ = rate
    rate_6_6 = add_comma(round(rate * 6.6,1))
    rate_6_7 = add_comma(round(rate * 6.7,1))
    rate_6_8 = add_comma(round(rate * 6.8,1))
    rate_6_9 = add_comma(round(rate * 6.9,1))
    rate_7 = add_comma(round(rate * 7,1)) 
    date = datetime.now().strftime("%d/%m/%Y")

    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
   
    
    payload = {
        "messaging_product":"whatsapp",
        "recipient_type":"individual",
        "to":reciever,
        "type":"template",
        "template":{
        "name":"rate_review",
        "language":{
        "code":"en"
        },
        "components":[
        {
        "type":"body",
        "parameters":[

        {
        "type":"text",
        "parameter_name":"base",
        "text":base
        },
        {
        "type":"text",
        "parameter_name":"rate",
        "text":rate
        },
        {
        "type":"text",
        "parameter_name":"rate_",
        "text":rate_
        },
        {
        "type":"text",
        "parameter_name":"rate_6_6",
        "text": rate_6_6
        },
        {
        "type":"text",
        "parameter_name":"rate_6_7",
        "text":rate_6_7
        },
        {
        "type":"text",
        "parameter_name":"rate_6_8",
        "text":rate_6_8
        },
        {
        "type":"text",
        "parameter_name":"rate_6_9",
        "text":rate_6_9
        },
        {
        "type":"text",
        "parameter_name":"rate_7",
        "text":rate_7
        },
        {
        "type":"date",
        "parameter_name":"rate_7",
        "text":date
        }

        ] 
        }]
        }}
    response = requests.post(url, headers=headers, json=payload)
    return response




def convert_whatsapp_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp)).astimezone()

def get_message(data):

    context = 'medical_practitioner'
    messages = data['entry'][0]['changes'][0]['value']['messages'][0]
    sender = messages['from']
    message_type = messages['type']
    record_format = 'text'
    action = ''
    content = ''


    if message_type == 'text':
        content = messages['text']['body'].strip()

        if len(content) < 10 and ":" not in content:
            action = 'get_rate'
            content = content.split(" ")
            if len(content) == 2:
                base,_ = content
                content = {'needed':base.upper()}
        else:
            content_dic = {}
            elems = content.split('\n')

            if len(elems) > 1:
                for elem in elems:
                    if ':' in elem:
                        key, value = elem.split(':', 1)
                        if key.strip() == 'action':
                            action = value.strip()
                        elif key.strip() in ['amount','usd_rate','usd_price','naira_rate','paid_amount']:
                            content_dic[key.strip()] = float(value.strip().replace(',',''))
                        else:
                            content_dic[key.strip()] = value.strip()
                content = content_dic

    else:
        content = messages[message_type]['id']
        record_format = messages[message_type]['mime_type'].split('/')[1]

    id = messages['id']
    timestamp = messages['timestamp']
    verify_context = messages.get('context')

    if verify_context:
        context = 'patient'
    return {'record_type':message_type, 'context':context,
            'content':content,'record_id':id,
            'action':action, 
            "timestamp": convert_whatsapp_timestamp(timestamp),
            'record_format':record_format, 'sender':sender}
    

def get_whatsapp_api_files(file_id):
    url = f"https://graph.facebook.com/v22.0/{file_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        url = data['url']
        response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error fetching API files: {response.status_code}")



# {'object': 'whatsapp_business_account', 
#  'entry': [{'id': '1186813426403332', 
#             'changes': [{'value': {'messaging_product': 'whatsapp', 
#                                    'metadata': {'display_phone_number': '15551920032', 'phone_number_id': '988162111037642'},
#                                     'contacts': [{'profile': {'name': 'EMEKA ONWUEPE'}, 'wa_id': '2348132180216'}],
#                                       'messages': [{'from': '2348132180216', 
#                                                     'id': 'wamid.HBgNMjM0ODEzMjE4MDIxNhUCABIYIEFDRjIzM0Q4NjY3RkFGQzhBQzlCMjdGNzk5REJDNzI1AA==', 
#                                                     'timestamp': '1767243880', 
#                                                     'text': {'body': 'Hello'}, 'type': 'text'}]}, 'field': 'messages'}]}]}


# {'record_type': 'text', 'context': 'medical_practitioner', 
#  'content': 'Hello', 
#  'record_id': 'wamid.HBgNMjM0ODEzMjE4MDIxNhUCABIYIEFDRjIzM0Q4NjY3RkFGQzhBQzlCMjdGNzk5REJDNzI1AA==', 
#  'timestamp': datetime.datetime(2026, 1, 1, 6, 4, 40, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600), 'W. Central Africa Standard Time')),
#    'record_format': 'text', 'sender': '2348132180216'}