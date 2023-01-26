from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import json
from .db import database, client
from .utils import pwd_context, output_format
# Create your views here.

def myview(request):
    # url = reverse('view_post', args=[23425678])
    # print(url)
    
    return HttpResponse("hsdf")




def user_profile(request):
    print(request.id)
    if request.id:
        user = database['User'].find_one({'_id' : request.id})
    
    print(user)
    # out = [i for i in user]
    return JsonResponse(output_format(message="Success!", data=user))


@api_view(['POST'])
def change_password(request):
    if request.id:
        data = request.data
        print(data)
        user = database['User'].find_one({'_id' : request.id})
        print(user)
        if pwd_context.verify(data['currentPassword'], user['password']):

            new_password = pwd_context.hash(data['newPassword'])

            database['User'].update_one(filter={
                '_id' : request.id},update=    # filtering user by email
            {'$set' : {"password" : new_password}}   # updating password
            )
            return JsonResponse(output_format(message='Success!'))

        else:
            return JsonResponse(output_format(message= "Wrong password."))
    

    # def post(self, request):
    #     print(request.data)
    #     return JsonResponse({"sdfg":4})


# @api_view(['GET'])
# def user_view(request, view_kwargs):
#     if request.method == 'GET':   


    
    # url = reverse('view_post', args=[23425678])
    # print(url)
        # result2 = database['user'].find({'email'})
        # User(id="user001", email = "abc@112.com", password='dddf', name='rja').save()
        # User(id="user002", email = "abc@12.com", password='dddf', name='rja').save()
        # for i in re   
        # users = User.objects.all()
        # result = database.list_collection_names()
        # print(result)
        # print("heeeellloo", users)
        # user_serializer = UserSerializer(users, many=True)
        # data = [dict(doc) for doc in user_serializer.data]
        # print('non-json', data)
        # data = json.dumps(data)
        # print("json_str    ", data)
        # # json_objects = []

        # # for od in user_serializer.data:
        # #     json_objects.append(json.dumps(dict(od)))

        # print("jsooooopn", json_objects)
        # print(user_serializer.data)

        # print('hee')

