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
    print(response.text)
    return response

def convert_whatsapp_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp)).astimezone()

def get_message(data):
    context = 'medical_practitioner'
    messages = data['entry'][0]['changes'][0]['value']['messages'][0]
    sender = messages['from']
    message_type = messages['type']
    record_format = 'text'
    if message_type == 'text':
        content = messages['text']['body']
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

