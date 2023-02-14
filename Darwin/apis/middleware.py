# User defined middleware for checking user tokens
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, JsonResponse
import jwt
import datetime
from apis.db import database, jwt_secret
from django.urls import resolve
from .utils import output_format
import base64


class AuthenticateMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        # APIs going through middleware
        self.allowed_apis = [
                        'user-profile', 
                        'change-password',
                        'admin-supplier',
                        'admin-category-type',
                        'admin-category',
                        'admin-product',
                        'admin-purchase',
                        'customer-address',
                        'product-discount',
                        'customer-order',
                        'add-to-cart',
                        'reset-password',
                        'admin-cat-type-to-category',
                        'admin-cat-to-product',
                        'cart',
                        'get-payment',
                        'cart-count',
                        'checkout-user-info',
                        'check-discount-code',
                        'verify-order'
                    ]
        # One-time configuration and initialization.

    def __call__(self, request):

        #getting name of the view
        url = resolve(request.path_info)
        view_name = url.view_name
        print("View name : ", view_name)

        if view_name in self.allowed_apis:

            #grabbing token
            try:
                token = request.headers['Authorization'].split()[1].strip('\"')
            except:
                return JsonResponse(output_format(message='Token not found!'))
            
            #trying to decode base64 token
            try:
                if view_name == 'reset-password':
                    token = base64.b64decode(token).decode()
            except:
                return JsonResponse(output_format(message='Token corrupted.'))
            
            #decoding token
            result = AuthenticateMiddleware.has_key(token)

            if type(result) == JsonResponse:
                return result
        
            if result is not None:

                print("has_key : ", result)
                #checking if expired
                if datetime.datetime.fromtimestamp(result['exp']) > datetime.datetime.now():
                    
                    user = database['User'].find_one({'_id': result['id']['id'], 'role': result['id']['role']})
                    
                    if user is not None:
                        request.id = user['_id']
                        request.role = user['role']
                    else:
                        return JsonResponse(output_format(message='User not found with received token.'))
                    # request['email'] = result['id']
            else:
                return JsonResponse(output_format(message="Token Expired!"), status = 200)

    
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    def has_key(token:str):
        try:
            return jwt.decode(token, jwt_secret, algorithms='HS256')
        except jwt.exceptions.ExpiredSignatureError as exp_err:
            return None
        except Exception:
            return JsonResponse(output_format(message='Token corrupted.'))
    
    # def process_request(self, request):
        # url = resolve(request.path_info)
        # view_name = url.func.view_class.__name__
        # print(view_name)
        # # 
        # if view_name in self.allowed_apis:
        #     print('hhhhh')
        #     #grabbing token
        #     if request.headers.get('Authorization'):
        #         token = request.headers['Authorization'].split()[1]

        #     #decoding token
        #     result = AuthenticateMiddleware.has_key(token)
        #     print(result)
        

        #     #checking if expired
        #     if datetime.datetime.fromtimestamp(result['exp']) > datetime.datetime.now():
                
        #         view_kwargs = {'id' : result['id']}
        #         # request['email'] = result['id']
        #         request.req_id = result['id']
        #         print(request)
        #         print()
                
        #         # user = database['User'].find_one({'email' : result['id']})
        #         # if user is not None:
        #             # pass
                
        #     else:
        #         return JsonResponse(data={"error" : "Token expired!"}, status = 213)
        # # return HttpResponse("damm", status = 401)
    
