from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from apis.models import User
from apis.serializers import UserSerializer
import json
from mongo_auth.db import database, client
# Create your views here.

def myview(request):
    # url = reverse('view_post', args=[23425678])
    # print(url)
    
    return HttpResponse("hsdf")


@api_view(['GET'])
def user_view(request):
    # url = reverse('view_post', args=[23425678])
    # print(url)
    if request.method == 'GET':
        # User(id="user001", email = "abc@112.com", password='dddf', name='rja').save()
        # User(id="user002", email = "abc@12.com", password='dddf', name='rja').save()

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
        pass
        # return JsonResponse(, safe=False)
    