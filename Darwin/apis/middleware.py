# User defined middleware for checking user tokens
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, JsonResponse
import jwt
import datetime
from apis.db import database, jwt_secret
from django.urls import resolve
from .utils import output_format


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

            #decoding token
            result = AuthenticateMiddleware.has_key(token)
            print(JsonResponse)
            if type(result) == JsonResponse:
                return result
        
            if result is not None:

                print("has_key : ", result)
                #checking if expired
                if datetime.datetime.fromtimestamp(result['exp']) > datetime.datetime.now():
                    
                    
                    request.id = result['id']['id']
                    request.role = result['id']['role']
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
    
