import uuid
import jwt
from passlib.context import CryptContext
from .db import jwt_secret, auth_collection
from .db import database
from Darwin.settings import FIREBASECONFIG
from django.core.files.storage import default_storage
import pyrebase

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


#for formatting output in json response
def output_format(status=200, message='', data={}):
    response = {"status" : status, "message":message, "data" : data}
    return response

# def parse_value(val = , out=int):
#     return out(val)


def firebase_image_upload(request, id):

    #setting up firebase connection
    firebase = pyrebase.initialize_app(FIREBASECONFIG)
    storage = firebase.storage()
    for i in request.FILES.values():
        pass

        # default_storage.