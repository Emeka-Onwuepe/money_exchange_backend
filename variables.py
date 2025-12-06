
# phone_id = '613209525219011' 
# VERIFY_TOKEN = '01948ea0-dc55-7b76-ae95-6bc44cc9f7e9'
# ngrok = 'https://76aa-102-88-111-36.ngrok-free.app'
# token ='EAAOeechl1owBO1AGtc5K3EmuWwCXcPlHesJU0FZBzditBOZAwUz6fgySIJG8lwMaDYbJZB4LJgq0hQMQL9TZBVDYAZCmbJrw7tgaFPz3lJcdNl8KtCybC17PdaGt4Masp7tFYZBueJv35OnZAjBO0ZB3ZAumyZCvPYbTVcfxIv2g2lWnYnvkxapFmdKKe2ntRojv9OyvZBZC7LDdEZAX1ZB1N0OfYZB4W6XzspWDURPLUcZD'


import os
# Variables for the Django application settings
# These variables are typically set in the environment for security and flexibility
phone_id = os.environ.get("phone_id")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
token = os.environ.get("token")