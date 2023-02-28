from rest_framework.decorators import api_view
from .utils import create_unique_object_id, pwd_context, output_format
from .db import database, auth_collection, fields, jwt_life, jwt_secret
import jwt
import datetime
from . import messages
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
import time


@api_view(["POST"])
def signup(request):

    data = request.data if request.data is not None else {}     #grabbing data from request
    print(data)
    if data == {}:
        return JsonResponse(output_format(message='Didn\'t receive signup data.'))
    signup_data = {"_id": create_unique_object_id()}
    all_fields = fields + ("role", "name")
    

    # preparing signup data
    for field in all_fields:
        if field in data:
            if field == 'email':
                data['email'] = data['email'].lower()
            signup_data[field] = data[field]
        else:
            return JsonResponse(output_format(message='Wrong data format.'))
    signup_data["password"] = pwd_context.hash(signup_data["password"])       #hashing password
    
    # checking whether email already exists or not
    if database[auth_collection].find_one({"email": signup_data['email'].lower()}) is None:
        try:
        # inserting data
            database[auth_collection].insert_one(signup_data)
            return JsonResponse(output_format(message='Success!'))
        except:
            return JsonResponse(output_format(message='User not signed up.'))
    else:
        return Response(output_format(message='User already exists.'))
    


@api_view(["POST"])
def login(request):
    data = request.data if request.data is not None else {}
    if data is None:
        return JsonResponse(output_format(message='Didn\'t receive login data.'))
    email = data['email'].lower()
    password = data['password']
    if "@" in email:
        user = database[auth_collection].find_one({"email": email})
    else:
        return JsonResponse(output_format(message='Wrong email format.'))

    
    if user is not None:
        # if password == user["password"]:
        if pwd_context.verify(password, user["password"]):
            
            # print(user['password'])

            #making of token

            token = jwt.encode({'id': {'id':user['_id'],'role':user['role']},
                                'exp': datetime.datetime.now() + datetime.timedelta(
                                    days=jwt_life)},
                                jwt_secret, algorithm='HS256')
            if type(token) == str:
            # print("hedfdfdfllo", token)
            # time.sleep(10)
            #decoding of token
                # result = jwt.decode(token, jwt_secret, algorithms='HS256')

            # print("myyy result: ", result)
                return JsonResponse(output_format(message='Success!', data={"token":token}))
            else:
                return JsonResponse(output_format(message='Token not created.'))
        else:
            return JsonResponse(output_format(message='Incorrect password!'))
    else:
        return JsonResponse(output_format(message='User not found.'))

