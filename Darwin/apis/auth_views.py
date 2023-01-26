from rest_framework.decorators import api_view
from .utils import create_unique_object_id, pwd_context, output_format
from .db import database, auth_collection, fields, jwt_life, jwt_secret, secondary_username_field
import jwt
import datetime
from . import messages
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import time


@api_view(["POST"])
def signup(request):
    try:
        data = request.data if request.data is not None else {}
        # print(data)
        
        signup_data = {"_id": create_unique_object_id()}
        all_fields = set(fields + ("email", "password"))
        # print(all_fields)
        if secondary_username_field is not None:
            all_fields.add(secondary_username_field)
        for field in set(fields + ("email", "password")):
            if field in data:
                signup_data[field] = data[field]
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"error_msg": field.title() + " does not exist."})
        signup_data["password"] = pwd_context.hash(signup_data["password"])       #hashing password   
        for key in data.keys():
            if key not in signup_data.keys():
                signup_data[key] = data[key]
        if database[auth_collection].find_one({"email": signup_data['email']}) is None:
            if secondary_username_field:
                if database[auth_collection].find_one({secondary_username_field: signup_data[secondary_username_field]}) is None:
                    database[auth_collection].insert_one(signup_data)
                    res = {k: v for k, v in signup_data.items() if k not in ["_id", "password"]}

                    res
                    return Response(status=status.HTTP_200_OK,
                                    data={"data": res})
                else:
                    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    data={"data": {"error_msg": messages.user_exists_field(secondary_username_field)}})
            else:
                database[auth_collection].insert_one(signup_data)
                res = {k: v for k, v in signup_data.items() if k not in ["_id", "password"]}
                return Response(status=status.HTTP_200_OK,
                                data=output_format(message='Success!', data={}))
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                            data=output_format(message='User already exists with this email.'))
    except ValidationError as v_error:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'success': False, 'message': str(v_error)})
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={"data": {"error_msg": str(e)}})


@api_view(["POST"])
def login(request):
    try:
        data = request.data if request.data is not None else {}
        username = data['email']
        password = data['password']
        if "@" in username:
            user = database[auth_collection].find_one({"email": username})
        else:
            if secondary_username_field:
                user = database[auth_collection].find_one({secondary_username_field: username}, {"_id": 0})
            else:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={"data": {"error_msg": messages.user_not_found}})
        
        if user is not None:
            # if password == user["password"]:
            if pwd_context.verify(password, user["password"]):
                
                # print(user['password'])
                #making of token
                token = jwt.encode({'id': user['_id'],
                                    'exp': datetime.datetime.now() + datetime.timedelta(
                                        hours=2)},
                                   jwt_secret, algorithm='HS256')
                # print("hedfdfdfllo", token)
                # time.sleep(10)
                #decoding of token
                    # result = jwt.decode(token, jwt_secret, algorithms='HS256')

                # print("myyy result: ", result)
                return Response(status=status.HTTP_200_OK,
                                data=output_format(message='Success!', data={"token":token}))
            else:
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={"error_msg": messages.incorrect_password})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={"data": {"error_msg": messages.user_not_found}})
    except ValidationError as v_error:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'success': False, 'message': str(v_error)})
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={"data": {"error_msg": str(e)}})
