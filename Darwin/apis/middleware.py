# User defined middleware for checking user tokens
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import jwt
import datetime


class AuthenticateMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_apis = ['user', 'myview']
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print(request.headers)
        print('\n\n hello \n\n')
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    def has_key(token:str) -> bool:
        jwt_secret = 'secret'
        result = jwt.decode(token, jwt_secret, algorithms='HS256')
        return result
    
    def process_view(self, request, view_func, view_args, view_kwargs):

        if request.headers.get('Authorization'):
            token = request.headers['Authorization'].split()[1]
        
        
        if view_func.__name__ in self.allowed_apis:
            result = AuthenticateMiddleware.has_key(token)
            print(result)
            if datetime.datetime.fromtimestamp(result['exp']) > datetime.datetime.now():
                ...

        
        # return HttpResponse("damm", status = 401)

    
