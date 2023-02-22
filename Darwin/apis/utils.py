import uuid
import jwt
import base64
import string
import secrets
from passlib.context import CryptContext
from .db import jwt_secret, auth_collection
from .db import database
from Darwin.settings import FIREBASECONFIG, MAIL_SERVICE_CONFIGS
from django.core.files.storage import default_storage
import pyrebase
import smtplib
from email.mime.text import MIMEText


pwd_context = CryptContext(
    default="django_pbkdf2_sha256",
    schemes=["django_argon2", "django_bcrypt", "django_bcrypt_sha256",
             "django_pbkdf2_sha256", "django_pbkdf2_sha1",
             "django_disabled"])


def create_unique_object_id():
    unique_object_id = "ID-{uuid}".format(uuid=uuid.uuid4())
    return unique_object_id


# Check if user if already logged in
def login_status(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    data = jwt.decode(token, jwt_secret, algorithms=['HS256'])
    user_obj = None
    flag = False
    user_filter = database[auth_collection].find({"id": data["id"]}, {"_id": 0, "password": 0})
    if user_filter.count():
        flag = True
        user_obj = list(user_filter)[0]
    return flag, user_obj


def convert_structure(data):
    new_data = []
    for item in data:
        existing_prod = None
        for new_item in new_data:
            if new_item['prod_id'] == item['prod_id']:
                existing_prod = new_item
                break
        size, qty = list(item['prod_qty'].keys())[0], list(item['prod_qty'].values())[0]
        if existing_prod:
            size, qty = list(item['prod_qty'].keys())[0], list(item['prod_qty'].values())[0]
            existing_prod['prod_qty'][size] = qty
        else:
            new_data.append({
                'prod_id': item['prod_id'],
                'prod_qty': {
                    size: qty 
                }
            })
    return new_data


#for formatting output in json response
def output_format(status=200, message='', data={}):
    response = {"status" : status, "message":message, "data" : data}
    return response


# for sending mails
def send_email(subject, body, recipients):
    print(body)
    msg = MIMEText(body, _subtype='html')
    print(msg)
    msg['Subject'] = subject
    msg['From'] = MAIL_SERVICE_CONFIGS['sender']
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL(MAIL_SERVICE_CONFIGS['smtp_server'], MAIL_SERVICE_CONFIGS['smtp_port'])
    smtp_server.login(MAIL_SERVICE_CONFIGS['sender'], MAIL_SERVICE_CONFIGS['password'])
    smtp_server.sendmail(MAIL_SERVICE_CONFIGS['sender'], recipients, msg.as_string())
    smtp_server.quit()

def firebase_image_upload(request, id):

    #setting up firebase connection
    firebase = pyrebase.initialize_app(FIREBASECONFIG)
    storage = firebase.storage()
    for i in request.FILES.values():
        pass

        # default_storage.

def random_str(length:int=5) -> str:
    alphabet = string.ascii_letters + string.digits
    random_str = ''.join(secrets.choice(alphabet) for i in range(length))
    return random_str.lower()

def base64decode(encoded_str:str) -> str:
    sample_string_bytes = base64.b64decode(encoded_str.encode('ascii'))
    sample_string = sample_string_bytes.decode("ascii")
    
    return sample_string