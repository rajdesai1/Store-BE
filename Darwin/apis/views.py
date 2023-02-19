import os
import json
import random
import base64
import requests
import datetime

import jwt
import razorpay
import pyrebase
import pandas as pd
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.files.storage import default_storage

from .db import database, jwt_secret
from Darwin.settings import FIREBASECONFIG, RAZORPAY_CONFIGS, MEDIA_ROOT
from .utils import (pwd_context, output_format, create_unique_object_id,
                    send_email, convert_structure, base64decode)

# Create your views here.

def myview(request):
    # url = reverse('view_post', args=[23425678])
    # print(url)
    
    return HttpResponse("<h1 style='font-size: 100px; font-family:system-ui;'>Hah! Nothing here.</h1>")


@api_view(['GET', 'PATCH'])
def user_profile(request):
    if request.method == 'GET':
        print(request.id)
        print(request.role)
        if request.id:
            user = database['User'].find_one({'_id' : request.id})
        
        print(user.pop('password'))
        # out = [i for i in user]
        return JsonResponse(output_format(message="Success!", data=user))
    
    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
                try:
                    data = request.data.dict()
                    print(data)
                    if data.get('mobile_no') is not None:
                        data['mobile_no'] =  int(data['mobile_no'])

                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                try:
                    result = database['User'].update_one(filter={'_id': user['_id']}, update= {"$set":data})
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Update failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))




@api_view(['GET'])
def checkout_user_info(request):
    
    if request.method == 'GET':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            #getting user details and address details
            data = database['User'].aggregate([
                            {
                              '$match': {'_id': user['_id']}
                            },
                            {
                            "$lookup":
                                {
                                    "from": "Ship-add",
                                    "localField": "_id",
                                    "foreignField": "user_id",
                                    "as": "Shipadd"
                                }
                            },
    
                            {
                              '$project':
                                {
                                  'email':1,
                                  'name':1,
                                  'mobile_no':1,
                                  'Shipadd_label':1,
                                  'Ship-add': {
                                '$filter': {
                                  'input': "$Shipadd",
                                  'as': "address",
                                  'cond': { '$eq': ["$$address.is_deleted", False] }
                                }
                            }
                            }},
                            {
                              '$project': {
                                  'Ship-add.is_deleted': False,
                                  'Ship-add.user_id': False
                              }
                            },
                            {
                              "$addFields": {
                                "Ship-add": {
                                  "$map": {
                                    'input': "$Ship-add",
                                    'as': "addr",
                                    'in': {
                                      '$mergeObjects': [
                                        "$$addr",
                                        {
                                          "Shipadd_label": {
                                            '$concat': [
                                              "$$addr.house_no", ", ",
                                              "$$addr.area_street", ", ",
                                              "$$addr.city", ", ",
                                              "$$addr.state", " - ",
                                              { '$toString': "$$addr.pincode" }
                                            ]
                                          }
                                        }
                                      ]
                                    }
                                  }
                                }
                              }
                            }])
            data = list(data)
            # print(list(data))
            if not data:
                return JsonResponse(output_format(message='User doesn\'t exist.'))
            else:
                # print(list(data)[0])
                return JsonResponse(output_format(message='Success!', data=data[0]))
        else:
            return JsonResponse(output_format(message='User not customer.'))
            

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


@api_view(['GET'])
def navbar_shop_category(request):

    
        cats = database['Category-type'].find({'is_deleted': False, 'active': True}, {"is_deleted": 0})
        out = [i for i in cats]
        print(out)
        print('s')
        return JsonResponse(output_format(data=out))


@api_view(['GET', 'POST', 'DELETE', 'PATCH'])
def supplier(request, _id=None):

##### for adding suppliers from admin panel(one supplier)
    if request.method == 'POST':
        
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        # checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            data = request.data.dict()

            # converting fields into int
            try:
                print(data['mobile_no'])
                data['mobile_no'] = int(data['mobile_no'])
                print(data['pincode'])
                
                data['pincode'] = int(data['pincode'])
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
            
            #inserting data
            try:
                data['_id'] = create_unique_object_id()
                data['is_deleted'] = False
                database['Supplier'].insert_one(data)
            except:
                return JsonResponse(output_format(message='Supplier not inserted.'))
            

            return JsonResponse(output_format(message='Success!'))
        else:
            return JsonResponse(output_format(message='User not admin.'))
        
##### for fetching suppliers in admin panel      
    elif request.method == 'GET':

        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:

                #getting and returning all the suppliers from the db
                try:
                    data = database['Supplier'].find({"is_deleted" : False}, {"is_deleted": 0})
                    data = [i for i in data]
                    print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Suppliers not fetched.'))

            # path parameter available
            else:
                try:
                    data = database['Supplier'].find_one({'_id': _id, 'is_deleted': False}, {"is_deleted": 0})
                    if data is None:
                        return JsonResponse(output_format(message='Supplier doesn\'t exist.'))
                    else:
                        return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Supplier not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### delete supplier from admin panel
    elif request.method == 'DELETE':

        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Supplier id not received.'))
            else:
                supplier = database['Supplier'].find_one({'_id': _id, "is_deleted": False})
                if supplier is None:
                    return JsonResponse(output_format(message='Supplier not found.'))
                
                purchase = database['Purchase'].find_one({'supp_id': _id})
                pass
                if purchase is not None:
                    return JsonResponse(output_format(message='Supplier not deleted. Associated purchases present.'))
                else:
                    database['Supplier'].update_one(filter={'_id':_id}, update={'$set': {'is_deleted': True}})
                    return JsonResponse(output_format(message='Success!'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### updating supplier details from admin panel   
    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Supplier id not received.'))

            else:
                supplier = database['Supplier'].find_one({'_id': _id, "is_deleted": False})
                if supplier is None:
                    return JsonResponse(output_format(message='Supplier not found.'))
                try:
                    data = request.data.dict()
                    print(data)
                    if data.get('mobile_no') is not None:
                        data['mobile_no'] = int(data['mobile_no'])
                    if data.get('pincode') is not None:
                        data['pincode'] = int(data['pincode'])
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                try:
                    result = database['Supplier'].update_one(filter={'_id': _id}, update= {"$set":data})
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Update failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))



@api_view(['POST', 'GET','DELETE', 'PATCH'])
def cat_type(request, _id=None):

##### for adding category type from admin panel
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            data = request.data.dict()
            #checking if cat_type already exists
            if database['Category-type'].find_one({"cat_type": data['cat_type']}) is None:

                #checking data format
                try:
                    data['active'] =  True if (data['active'] in ('true','True')) else False
                    data['cat_type'] = data['cat_type']
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))

                #inserting data
                try:
                    data['_id'] = create_unique_object_id()
                    data['is_deleted'] = False
                    database['Category-type'].insert_one(data)
                    return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Category-type not inserted.'))
            else:
                return JsonResponse(output_format(message='Category-type already exists.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### for getting all categories type in admin panel
    elif request.method == 'GET':

        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:

                #getting and returning all the category-type from the db
                try:
                    data = database['Category-type'].find({'is_deleted' : False}, {"is_deleted": 0})
                    data = [i for i in data]
                    print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Category-type not fetched.'))
            
            # path parameter available
            else:
                try:
                    data = database['Category-type'].find_one({'_id': _id, 'is_deleted' : False}, {"is_deleted": 0})
                    if data is None:
                        return JsonResponse(output_format(message='Category-type doesn\'t exist.'))
                    else:
                        return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Category-type not fetched.'))    
        else:
            return JsonResponse(output_format(message='User not admin.'))
    
##### delete category-type from admin panel
    elif request.method == 'DELETE':

        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category-type id not received.'))
            else:
                category_type = database['Category-type'].find_one({'_id': _id, "is_deleted": False})
                if category_type is None:
                    return JsonResponse(output_format(message='Category-type not found.'))
                
                category = database['Category'].find_one({'cat_type_id': _id, "is_deleted": False})
                
                if category is not None:
                    return JsonResponse(output_format(message='Category-type not deleted. Associated category present.'))
                else:
                    database['Category-type'].update_one(filter={'_id':_id}, update={'$set': {'is_deleted': True}})
                    return JsonResponse(output_format(message='Success!'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### updating category-type from admin panel   
    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category-type id not received.'))

            else:
                category_type = database['Category-type'].find_one({'_id': _id, "is_deleted": False})
                if category_type is None:
                    return JsonResponse(output_format(message='Category-type not found.'))
                try:
                    data = request.data.dict()
                    print(data)
                    if data.get('active') is not None:
                        data['active'] =  True if (data['active'] in ('true','True')) else False

                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                try:
                    result = database['Category-type'].update_one(filter={'_id': _id}, update= {"$set":data})
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Update failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


@api_view(['GET'])
def admin_cat_type_to_category(request, _id=None):
    
##### for getting categories using category type from admin panel
    if request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category-type id not received.'))
            else:
                
                if database['Category-type'].find_one({'_id': _id, 'is_deleted' : False}, {"is_deleted": 0}) is None:
                    return JsonResponse(output_format(message='Category-type doesn\'t exist.'))
                
                out = database["Category-type"].aggregate(
                    [
                        {
                            "$lookup": {
                                "from": "Category",
                                "localField": "_id",
                                "foreignField": "cat_type_id",
                                "as": "Category",
                            }
                        },
                        {"$match": {"_id": _id, "is_deleted": False, "Category.is_deleted": False}},
                        {
                            "$project": {
                                "_id": 1,
                                "cat_type": 1,
                                "Category": {
                                    "$map": {
                                        "input": "$Category",
                                        "as": "catgory",
                                        "in": {
                                            "cat_id": "$$catgory._id",
                                            "cat_title": "$$catgory.cat_title"
                                        },
                                    }
                                },
                            }
                        },
                    ]
                )
                
                try:
                    data = out.next()
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Categories not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


@api_view(['POST', 'GET', 'DELETE', 'PATCH'])
def admin_category(request, _id=None):

##### for adding category from admin panel
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            data = request.data.dict()
            #checking if the same category already exists in same category type
            if database['Category'].find_one({'cat_title': data['cat_title'], 'cat_type_id':data['cat_type_id']}) is None:

                # checking whether cat-type exists or not 
                if database['Category-type'].find_one({'_id': data['cat_type_id']}) is None:
                    # ref = DBRef(collection='Category-type',database='mystore', id=data['cat_type_id'])
                    # doc = ref.as_doc()
                    # print(doc)
                    # print(dir(ref))
                    # print(ref)
                    return JsonResponse(output_format(message='Category-type doesn\'t exist.')) 

                #checking data format
                try:
                    data['active'] =  True if (data['active'] in ('true','True')) else False
                    data['cat_title'] = data['cat_title']
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))

                #inserting data
                try:
                    data['_id'] = create_unique_object_id()
                    data['is_deleted'] = False
                    database['Category'].insert_one(data)
                    return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Category not inserted.'))
            else:
                return JsonResponse(output_format(message='Category already exists.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### getting all categories in admin panel
    elif request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                #getting and returning all the category from the db
                try:
                    pipeline = [{
                            '$lookup':{
                                'from':'Category',
                                'localField':'_id',
                                'foreignField':'cat_type_id',
                                'as':'Category'
                            }
                        },
                        {
                            '$unwind':'$Category'
                        },
                        {
                            "$match": {'Category.is_deleted': False, 'is_deleted': False}
                        },
                        {
                            '$project': {
                                '_id':'$Category._id',
                                'cat_type_id': '$_id',
                                'cat_type': '$cat_type',
                                'active': '$Category.active',
                                'cat_title': '$Category.cat_title',
                                'cat_desc': "$Category.cat_desc",
                            }
                        }
                    ]

                    data = database['Category-type'].aggregate(pipeline=pipeline)
                    data = [i for i in data]
                    print(data)
                    print(len(data))

                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Category not fetched.'))
            # path parameter available
            else:
                try:
                    print(_id)
                    pipeline = [{
                            "$lookup": {
                                "from": "Category",
                                "localField": "_id",
                                "foreignField": "cat_type_id",
                                "as": "Category"
                            }
                            },
                            { "$unwind": "$Category" },
                            {
                            "$match": { "Category._id": _id, 'is_deleted': False, 'Category.is_deleted': False }
                            },
                            {
                                "$project": {
                                    "_id": "$Category._id",
                                    "cat_type_id": "$_id",
                                    "cat_type": "$cat_type",
                                    "active": "$Category.active",
                                    "cat_title": "$Category.cat_title",
                                }
                            },
                        ]
  
                    data = database['Category-type'].aggregate(pipeline=pipeline)
                    data = list(data)
                    # print(list(data))
                    if not data:
                        return JsonResponse(output_format(message='Category doesn\'t exist.'))
                    else:
                        # print(list(data)[0])
                        return JsonResponse(output_format(message='Success!', data=data[0]))
                except:
                    return JsonResponse(output_format(message='Category not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))
        
    elif request.method == 'DELETE':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            
            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category id not received.'))
            else:
                category_type = database['Category'].find_one({'_id': _id, "is_deleted": False})
                if category_type is None:
                    return JsonResponse(output_format(message='Category not found.'))
                
                product = database['Product'].find_one({'cat_id': _id, "is_deleted": False})
                
                if product is not None:
                    return JsonResponse(output_format(message='Category not deleted. Associated product present.'))
                else:
                    database['Category'].update_one(filter={'_id':_id}, update={'$set': {'is_deleted': True}})
                    return JsonResponse(output_format(message='Success!'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category id not received.'))

            else:
                category = database['Category'].find_one({'_id': _id, "is_deleted": False})
                if category is None:
                    return JsonResponse(output_format(message='Category not found.'))
                try:
                    data = request.data.dict()
                    print(data)
                    if data.get('active') is not None:
                        data['active'] =  True if (data['active'] in ('true','True')) else False

                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                try:
                    result = database['Category'].update_one(filter={'_id': _id}, update= {"$set":data})
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Update failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


@api_view(['GET'])
def admin_cat_to_product(request, _id=None):
    
##### for getting categories using category type from admin panel
    if request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category id not received.'))
            else:
                
                if database['Category'].find_one({'_id': _id, 'is_deleted' : False}, {"is_deleted": 0}) is None:
                    return JsonResponse(output_format(message='Category doesn\'t exist.'))
                
                out = database["Category"].aggregate(
                    [
                        {
                            "$lookup": {
                                "from": "Product",
                                "localField": "_id",
                                "foreignField": "cat_id",
                                "as": "Product",
                            }
                        },
                        {"$match": {"_id": _id, "is_deleted": False, "Product.is_deleted": False}},
                        {
                            "$project": {
                                "_id": 1,
                                "cat_title": 1,
                                "Product": {
                                    "$map": {
                                        "input": "$Product",
                                        "as": "product",
                                        "in": {
                                            "prod_id": "$$product._id",
                                            "prod_name": "$$product.prod_name",
                                        },
                                    }
                                },
                            }
                        },
                    ]
                )
                
                try:
                    data = out.next()
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Categories not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

                

@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
def admin_product(request, _id=None):

##### for uploading products from admin panel
    if request.method == 'POST':
        user = database['User'].find_one(filter={'_id':request.id})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            #checking whether category exists or not
            if database['Category'].find_one({'_id': request.POST['cat_id']}) is None:
                return JsonResponse(output_format(message='Category doesn\'t exist.'))

            #connecting to the firebase
            firebase = pyrebase.initialize_app(FIREBASECONFIG)
            storage = firebase.storage()
    

            #preparing data dict to upload into the db
            try:
                prod_id = create_unique_object_id()
                data = {}
                data['prod_name'] = request.POST['prod_name']
                data['cat_id'] = request.POST['cat_id']
                data['active'] = True if request.POST['active'] in ('true' or 'True') else False
                data['prod_desc'] = request.POST['prod_desc']
                data['created_at'] = datetime.datetime.now()
                data['prod_price'] = float(request.POST['prod_price'])
                data['prod_qty'] = {}
                data['prod_image'] = []

                if len(request.FILES) < 1:
                    return JsonResponse(output_format(message='Images not received.'))
                else:
                    #renaming all product images and uploading to firebase
                    for i, file in enumerate(request.FILES.values()):
                        filename, fileextension = os.path.splitext(file.name)
                        if fileextension not in ['.png', '.jpg', '.jpeg', '.webp']:
                            return JsonResponse(output_format(message='Uploaded file is not an image.'))
                        
                        new_name = f"{prod_id}-{str(i)}{fileextension}"
                        file.name = new_name
                        default_storage.save(new_name, file)        #saving to local storage before uploading to the cloud
                        
                        #uploading here
                        try:
                            storage.child(f'prod_image/{new_name}').put(f'{MEDIA_ROOT}/{new_name}')
                            default_storage.delete(new_name)        #deleting from local storage after uploading to the cloud
                            image_url = storage.child(f'prod_image/{new_name}').get_url(token=None)
                            data['prod_image'].append(image_url)
                        except:
                            return JsonResponse(output_format(message='Cloud upload failed.'))    
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
            
            #and finally inserting product to the db
            try:
                    data['_id'] = prod_id
                    data['is_deleted'] = False
                    database['Product'].insert_one(data)
                    return JsonResponse(output_format(message='Success!'))
            except:
                    return JsonResponse(output_format(message='Category not inserted.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### for getting products into admin panel
    elif request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                #getting and returning all the products from the db
                try:
                    pipeline = [{
                            '$lookup':{
                                'from':'Product',
                                'localField':'_id',
                                'foreignField':'cat_id',
                                'as':'Product'
                            }
                        },
                        {
                            '$unwind':'$Product'
                        },
                        {
                            "$match": {'Product.is_deleted': False, 'is_deleted': False}
                        },
                        {
                            '$project': {
                                '_id': '$Product._id',
                                'prod_name': '$Product.prod_name',
                                'cat_id':'$_id',
                                'cat_title': '$cat_title',
                                'active': '$Product.active',
                                'prod_price': '$Product.prod_price',
                                'prod_qty': '$Product.prod_qty',
                                'prod_desc': '$Product.prod_desc',
                                'created_at': '$Product.created_at',
                                'prod_image': '$Product.prod_image',
                            }
                        }
                    ]

                    data = database['Category'].aggregate(pipeline=pipeline)
                    data = [i for i in data]
                    print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Products not fetched.'))
            
            # path parameter available
            else:
                try:
                    print(_id)
                    data = database['Category-type'].aggregate([
                            {
                            "$lookup":
                                {
                                    "from": "Category",
                                    "localField": "_id",
                                    "foreignField": "cat_type_id",
                                    "as": "Category"
                                }
                            },
                            {
                                "$unwind": "$Category"
                            },
                            {
                            "$lookup":
                                {
                                    "from": "Product",
                                    "localField": "Category._id",
                                    "foreignField": "cat_id",
                                    "as": "Product"
                                }
                            },
                            {
                            "$unwind": "$Product"
                            },
                            {
                                "$match": {"Product._id": _id, 'is_deleted': False, 'Product.is_deleted': False}
                            },
                            {
                                "$project":
                                {
                                    "_id": "$Product._id",
                                    "prod_name": "$Product.prod_name",
                                    "prod_desc": "$Product.prod_desc",
                                    "prod_image": "$Product.prod_image",
                                    "prod_price": "$Product.prod_price",
                                    "cat_id" : "$Product.cat_id",
                                    "cat_title": "$Category.cat_title",
                                    "cat_type_id": "$Category.cat_type_id",
                                    "cat_type": "$cat_type",
                                    
                                }
                            }])
                    data = list(data)
                    if not data:
                        return JsonResponse(output_format(message='Product doesn\'t exist.'))
                    else:
                        return JsonResponse(output_format(message='Success!', data=data[0]))
                except:
                    return JsonResponse(output_format(message='Product not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

    elif request.method == 'PATCH':
        
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Category id not received.'))
            else:
                product = database['Category'].find_one({'_id': _id, "is_deleted": False})
                if product is None:
                    return JsonResponse(output_format(message='Category not found.'))
                try:
                    data = request.POST.get()
                    print(data)
                    
                    update = {}
                    if data.get('prod_price') is not None:
                        data['prod_price'] =  float(request.POST['prod_price'])
                    if data.get('active') is not None:
                        data['active'] =  True if (data['active'] in ('true','True')) else False
                    if data.get('prod_image') is not None:
                        update["$pull"] = { "prod_image": {"$inc": {'prod_image': [data.get('prod_image')]}} }
                        data.pop('prod_image')
                    update['$set'] = data

                    #renaming all product images and uploading to firebase
                    try:
                        next(request.FILES.values())
                        firebase = pyrebase.initialize_app(FIREBASECONFIG)
                        storage = firebase.storage()
                    except:
                        pass
                    
                    #updating data
                    for i, file in enumerate(request.FILES.values()):
                        filename, fileextension = os.path.splitext(file.name)
                        if fileextension not in ['.png', '.jpg', '.jpeg', '.webp']:
                            return JsonResponse(output_format(message='Uploaded file is not an image.'))
                        
                        new_name = f"{prod_id}-{str(i)}{fileextension}"
                        file.name = new_name
                        default_storage.save(new_name, file)        #saving to local storage before uploading to the cloud
                        
                        #uploading here
                        try:
                            storage.child(f'prod_image/{new_name}').put(f'mediafiles/{new_name}')
                            default_storage.delete(new_name)        #deleting from local storage after uploading to the cloud
                            image_url = storage.child(f'prod_image/{new_name}').get_url(token=None)
                            data['prod_image'].append(image_url)
                        except:
                            return JsonResponse(output_format(message='Cloud upload failed.'))    

                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                try:
                    result = database['Category'].update_one(filter={'_id': _id}, update= {"$set":data})
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Update failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

    if request.method == 'DELETE':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            
            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Product id not received.'))
            else:
                product = database['Product'].find_one({'_id': _id, "is_deleted": False})
                if product is None:
                    return JsonResponse(output_format(message='Product not found.'))

                # this will set is_deleted=True only if every size in prod_qty is 0 or prod_qty itself is empty
                result = database['Product'].update_one(
                    { 
                        "_id": _id, 
                        '$expr': { '$eq': [ 
                                { '$size': { '$objectToArray': "$prod_qty" } }, 
                                { '$size': { '$filter': { 'input': { '$objectToArray': "$prod_qty" }, 'cond': { '$eq': 
                                    [ "$$this.v", 0 ] } } } } 
                                ] 
                            } 
                    },
                    { '$set': { "is_deleted": True } })
                
                if result.modified_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Product not deleted. Associated quantity present.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


@api_view(['GET', 'PATCH'])
def admin_order(request, _id=None):
    
    if request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            #Query params contains filter for order's status
            query_params = request.GET.dict()
            order_status = query_params['order_status']
            try:
                # query to get all customer orders
                data = database["Order"].aggregate([
                        {
                            "$match": {'order_status': order_status}
                        },
                        {"$unwind": "$Order-details"},
                        {
                            "$project": {
                                "prod_id": "$Order-details.prod_id",
                                "prod_qty": {
                                    "$objectToArray": "$Order-details.prod_qty"
                                },
                                "add_id": 1,
                                "total_amount": 1,
                                "discount": 1,
                                "_id": 1,
                                "order_date": 1,
                                "Payment-details": 1
                            }
                        },
                        {"$unwind": "$prod_qty"},
                        {
                            "$project": {
                                "_id": 1,
                                "prod_id": "$prod_id",
                                "size": "$prod_qty.k",
                                "qty": "$prod_qty.v",
                                "add_id": 1,
                                "disc_id": 1,
                                "total_amount": 1,
                                "discount": 1,
                                "order_date": 1,
                                "Payment-details": 1
                            }
                        },
                        {
                            "$lookup": {
                                "from": "Product",
                                "localField": "prod_id",
                                "foreignField": "_id",
                                "as": "Product"
                            }
                        },
                        {"$unwind": "$Product"},
                        {
                            "$project": {
                                "add_id": 1,
                                "total_amount": 1,
                                "discount": 1,
                                "_id": 1,
                                "order_date": 1,
                                "Payment-details": 1,
                                "size": "$size",
                                "qty": "$qty",
                                "prod_name": "$Product.prod_name",
                                "prod_price": "$Product.prod_price",
                                'prod_desc': '$Product.prod_desc'
                            }
                        },
                        {
                            "$group": {
                                "_id": {
                                    "_id": "$_id",
                                    "add_id": "$add_id",
                                    "total_amount": "$total_amount",
                                    "discount": "$discount",
                                    "order_date": "$order_date",
                                    "Payment-details": "$Payment-details"
                                },
                                "Order_details": {
                                    "$push": {
                                        "prod_name": "$prod_name",
                                        "size": "$size",
                                        "qty": "$qty",
                                        "prod_price": "$prod_price",
                                        'prod_disc': '$prod_desc'
                                    }
                                }
                            }
                        },
                        {
                            "$lookup": {
                                "from": "Ship-add",
                                "localField": "_id.add_id",
                                "foreignField": "_id",
                                "as": "Ship-add"
                            }
                        },
                        {"$unwind": "$Ship-add"},
                        {
                            "$project": {
                                "_id": "$_id._id",
                                "add_id": "$_id.add_id",
                                "total_amount": "$_id.total_amount",
                                "discount": "$_id.discount",
                                "house_no": "$Ship-add.house_no",
                                "user_id": "$Ship-add.user_id",
                                "area_street": "$Ship-add.area_street",
                                "add_type": "$Ship-add.add_type",
                                "pincode": "$Ship-add.pincode",
                                "state": "$Ship-add.state",
                                "city": "$Ship-add.city",
                                "Payment-details": "$_id.Payment-details",
                                "order_date": "$_id.order_date",
                                "Order_details": "$Order_details"
                            }
                        },
                        {
                            "$lookup": {
                                "from": "User",
                                "localField": "user_id",
                                "foreignField": "_id",
                                "as": "User"
                            }
                        },
                        {"$unwind": "$User"},
                        {
                            "$project": {
                                "_id": "$_id",
                                "total_amount": "$total_amount",
                                "discount": "$discount",
                                "house_no": "$house_no",
                                "area_street": "$area_street",
                                "add_type": "$add_type",
                                "pincode": "$pincode",
                                "state": "$state",
                                "city": "$city",
                                "razorpay_payment_id": "$Payment-details.razorpay_payment_id",
                                "order_date": "$order_date",
                                "Order_details": 1,
                                "email": "$User.email",
                                "name": "$User.name",
                                "mobile_no": "$User.mobile_no"
                            }
                        },
                        { '$sort': { 'order_date': -1 } }
                    ])
           
                data = list(data)
                if not data:
                
                    return JsonResponse(output_format(message='Orders not found.'))
                else:
                    if order_status in ('Pending', 'Delivered'):
                        
                        client = razorpay.Client(auth=(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']), 
                                                        base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_SECRET'])))
                        for order in data:
                            razorpay_payment_id = order.get('razorpay_payment_id')
                            if razorpay_payment_id is not None:

                                output = client.payment.fetch(razorpay_payment_id)
                                
                                payment_method = output.get('method')
                                if payment_method == 'card':
                                    data['card_last4'] = output['card']['last4']
                                elif payment_method == 'upi':
                                    data['card_last4'] = output['upi_transaction_id']
                                order.pop('razorpay_payment_id')
                    return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Orders not fetched.'))

    elif request.method == 'PATCH':
         #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            if _id is None:
                return JsonResponse(output_format(message='Order id not received.'))
            else:

                data = request.data.dict()
                order_status = data.get('order_status')
                
                if order_status is not None:
                    result = database['Order'].update_one({'_id': _id}, {'$set': {'order_status': order_status}})
                    if result.matched_count == 1 and result.modified_count == 1:
                        return JsonResponse(output_format(message='Success'))
                    else:
                        return JsonResponse(output_format(message='Update failed.'))
                else:
                    return JsonResponse(output_format(message='Order status not received.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))
            
# # @api_view(['POST', 'GET'])
# # def admin_product(request, _id=None):

# ##### for uploading products from admin panel
#     if request.method == 'POST':
#         user = database['User'].find_one(filter={'_id':request.id})

#         #checking if user is admin
#         if user['role'] == 'admin' and user['_id'] == request.id:
#             print(request.body)
#             pass
#             data = json.loads(request.body)
#             pass
#             #checking whether category exists or not
#             if database['Category'].find_one({'_id': data['cat_id']}) is None:
#                 return JsonResponse(output_format(message='Category doesn\'t exist.'))

#             #connecting to the firebase
#             # firebase = pyrebase.initialize_app(FIREBASECONFIG)
#             # storage = firebase.storage()
    

#             #preparing data dict to upload into the db
#             try:
#                 print(data)
#                 prod_id = create_unique_object_id()
#                 data['prod_name'] = data['prod_name']
#                 data['cat_id'] = data['cat_id']
#                 data['active'] = data['active']
#                 data['prod_desc'] = data['prod_desc']
#                 data['created_at'] = datetime.datetime.now()
#                 data['prod_price'] = int(data['prod_price'])
#                 data['prod_qty'] = {}
#                 filelinks = data['prod_image']
#                 data['prod_image'] = []

#                 #renaming all product images and uploading to firebase
#                 for i, filelink in enumerate(filelinks):

                    
#                     fileextension = filelink.split('.')[-1]
#                     if fileextension not in ['png', 'jpg', 'jpeg', 'webp']:
#                         return JsonResponse(output_format(message='Uploaded file is not an image.'))
                    
#                     response = requests.get(filelink)


                    
#                     new_name = f"{prod_id}-{str(i)}.{fileextension}"
#                     with open(f'mediafiles/{new_name}', "wb") as f:
#                         f.write(response.content)
#                     # default_storage.save(new_name, file)        #saving to local storage before uploading to the cloud
                    
#                     #uploading here
#                     try:
#                         storage.child(f'prod_image/{new_name}').put(f'mediafiles/{new_name}')
#                         default_storage.delete(new_name)        #deleting from local storage after uploading to the cloud
#                         image_url = storage.child(f'prod_image/{new_name}').get_url(token=None)
#                         data['prod_image'].append(image_url)
#                     except:
#                         return JsonResponse(output_format(message='Cloud upload failed.'))    
#             except:
#                 return JsonResponse(output_format(message='Wrong data format.'))
            
#             #and finally inserting product to the db
#             try:
#                     data['_id'] = prod_id
#                     data['is_deleted'] = False
#                     database['Product'].insert_one(data)
#                     return JsonResponse(output_format(message='Success!'))
#             except:
#                     return JsonResponse(output_format(message='Category not inserted.'))
#         else:
#             return JsonResponse(output_format(message='User not admin.'))


# ##### for getting products into admin panel
#     if request.method == 'GET':
#         #fetching user data
#         user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

#         #checking if user is admin
#         if user['role'] == 'admin' and user['_id'] == request.id:

#             # checking for path parameters
#             if _id == None:
#                 #getting and returning all the products from the db
#                 try:
#                     pipeline = [{
#                             '$lookup':{
#                                 'from':'Product',
#                                 'localField':'_id',
#                                 'foreignField':'cat_id',
#                                 'as':'Product'
#                             }
#                         },
#                         {
#                             '$unwind':'$Product'
#                         },
#                         {
#                             '$project': {
#                                 '_id': '$Product._id',
#                                 'prod_name': '$Product.prod_name',
#                                 'cat_id':'$_id',
#                                 'cat_type': '$cat_title',
#                                 'active': '$Product.active',
#                                 'prod_price': '$Product.prod_price',
#                                 'prod_qty': '$Product.prod_qty',
#                                 'prod_desc': '$Product.prod_desc',
#                                 'created_at': '$Product.created_at',
#                                 'prod_image': '$Product.prod_image',
#                             }
#                         }
#                     ]

#                     data = database['Category'].aggregate(pipeline=pipeline)
#                     data = [i for i in data]
#                     print(data)
#                     return JsonResponse(output_format(message='Success!', data=data))
#                 except:
#                     return JsonResponse(output_format(message='Products not fetched.'))
            
#             # path parameter available
#             else:
#                 try:                
#                     pipeline = [{
#                             '$lookup':{
#                                 'from':'Product',
#                                 'localField':'_id',
#                                 'foreignField':'cat_id',
#                                 'as':'Product'
#                             }
#                         },
#                         {
#                             '$unwind':'$Product'
#                         },
#                         {
#                                 "$match": { "Product._id": _id }
#                         },
#                         {
#                             '$project': {
#                                 '_id': '$Product._id',
#                                 'prod_name': '$Product.prod_name',
#                                 'cat_id':'$_id',
#                                 'cat_type': '$cat_title',
#                                 'active': '$Product.active',
#                                 'prod_price': '$Product.prod_price',
#                                 'prod_qty': '$Product.prod_qty',
#                                 'prod_desc': '$Product.prod_desc',
#                                 'created_at': '$Product.created_at',
#                                 'prod_image': '$Product.prod_image',
#                             }
#                         }
#                     ]
  
#                     data = database['Category'].aggregate(pipeline=pipeline)
#                     if list(data) != []:
#                         data = list(data)
#                         print(list(data)[0])
#                         return JsonResponse(output_format(message='Product doesn\'t exist.'))
#                     else:
#                         return JsonResponse(output_format(message='Success!', data=data[0]))
#                 except:
#                     return JsonResponse(output_format(message='Product not fetched.'))
#         else:
#             return JsonResponse(output_format(message='User not admin.'))















@api_view(['POST', 'GET', 'PATCH'])
def admin_purchase(request, _id=None):

##### for uploading purchased products from admin panel
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            try:
                data = json.loads(request.body)     #loading body string to json data
                data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                return JsonResponse(output_format(message='Wrong data format.'))

            #checking whether supplier exists
            if database['Supplier'].find_one({'_id':data['supp_id'], "is_deleted": False}) is None:
                return JsonResponse(output_format(message='Supplier doesn\'t exist.'))
            
            #processing Purchase details
            for product_details in data['Purchase-details']:
                
                #checking whether product exists or not
                if database['Product'].find_one({'_id': product_details['prod_id']}) is None:
                    return JsonResponse(output_format(message='Product doesn\'t exist.'))
                
                # converting purchase details from received array to dictionary
                tmp = {item['size']: item['qty'] for item in product_details['purch_qty']}
                #adding purchased qty to the existing product
                prod_qty = {}
                for size, qty in tmp.items():
                    prod_qty[f'prod_qty.{size}'] = qty
                print(prod_qty)
                database['Product'].update_one({"_id": product_details['prod_id']},
                    {"$inc": prod_qty}
                )

            #inserting data
            try:
                data['_id'] = create_unique_object_id()
                database['Purchase'].insert_one(data)
                return JsonResponse(output_format(message='Success!'))
            except:
                return JsonResponse(output_format(message='Purchase not inserted.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

    elif request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
                
            # checking for path parameters
            if _id == None:
                #getting and returning all the products from the db
                try:
                    pipeline = [{
                            '$lookup':{
                                'from':'Purchase',
                                'localField':'_id',
                                'foreignField':'supp_id',
                                'as':'Purchase'
                            }
                        },
                        {
                            '$unwind':'$Purchase'
                        },
                        {
                            '$project': {
                                '_id': '$Purchase._id',
                                'supp_name': '$name',    #supplier name
                                'date': '$Purchse.date',
                                'total_amount': '$Purchase.total_amount',
                                'Purchase-details':'$Purchase.Purchase-details'
                            }
                        }
                    ]

                    data = database['Supplier'].aggregate(pipeline=pipeline)
                    data = [i for i in data]
                    print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Purchases not fetched.'))
            # path parameter available
            else:
                pipeline = [{
                            '$lookup':{
                                'from':'Purchase',
                                'localField':'_id',
                                'foreignField':'supp_id',
                                'as':'Purchase'
                            }
                        },
                        {
                            '$unwind':'$Purchase'
                        },
                        {
                            '$match' : {'Purchase._id': _id}
                        },
                        {
                            '$project': {
                                '_id': '$Purchase._id',
                                'supp_name': '$name',    #supplier name
                                'date': '$Purchse.date',
                                'total_amount': '$Purchase.total_amount',
                                'Purchase-details':'$Purchase.Purchase-details'
                            }
                        }
                    ]

                data = database['Supplier'].aggregate(pipeline=pipeline)
                data = list(data)
                if not data:
                    return JsonResponse(output_format(message='Purchase doesn\'t exist.'))
                else:
                    return JsonResponse(output_format(message='Success!', data=data[0]))
        else:
            return JsonResponse(output_format(message='User not admin.'))
    
##### for purchase 
    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Purchase id not received.'))
            
            # if id is receivied
            else:
                purchase = database['Purchase'].find_one({'_id': _id})
                if purchase is None:
                    return JsonResponse(output_format(message='Purchase not found.'))
                try:
                    data = json.loads(request.body)     #loading body string to json data
                    if data.get('date') is not None:
                        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    if data.get('supp_id') is not None:
                        #checking whether supplier exists
                        if database['Supplier'].find_one({'_id':data['supp_id'], "is_deleted": False}) is None:
                            return JsonResponse(output_format(message='Supplier doesn\'t exist.'))
                    
                    #adding purchased qty to the existing product
                    prod_qty = {}
                    
                    for purchased_product in data['Purchase-details']:
                        
                        
                        for prod in purchased_product.items():
                            
                            prod = database['Product'].find_one({'_id': prod['prod_id'], "is_deleted": False})
                            if prod is None:
                                return JsonResponse(output_format(message='Product doesn\'t exist.'))
                            

                        product = database['Product'].find_one(
                            filter={'_id': purchased_product['prod_id']})     #fetching product from product table

                        #checking whether product exists
                        if product is None:
                            return JsonResponse(output_format(message='Product doesn\'t exist.'))
                        
                        
                            # for purchase_product  in purchase['Purchase-details']:
                            #     prod_qty[f'prod_qty.{size}'] = qty
                            # print(prod_qty)
                            # database['Product'].update_one({"_id": product_details['prod_id']},
                            # {"$inc": prod_qty}
                            # )
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))            
                


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
def customer_address(request, _id=None):

##### for addding customer's address   
    if request.method == 'POST':
        
        #fetching customer details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            request_data = request.data.dict()
            data = {}

            #checking data format
            try:
                data['user_id'] = user['_id']
                data['house_no'] = request_data['house_no']
                data['area_street'] = request_data['area_street']
                data['add_type'] = request_data['add_type']
                data['pincode'] = int(request_data['pincode'])
                data['state'] = request_data['state']
                data['city'] = request_data['city']

            except:
                return JsonResponse(output_format(message='Wrong data format.'))

            #inserting data
            try:
                data['_id'] = create_unique_object_id()
                data['is_deleted'] = False
                database['Ship-add'].insert_one(data)
                return JsonResponse(output_format(message='Success!'))
            except:
                return JsonResponse(output_format(message='Address not inserted.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))

##### for getting all addresses for a user
    elif request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                #getting and returning all the products from the db
                try:
                    data = database['Ship-add'].find({"user_id": user['_id'], 'is_deleted': False}, {"is_deleted": 0})
                    data = [i for i in data]
                    print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Addresses not fetched.'))
            
            # path parameter available
            else:
                try:
                    data=database['Ship-add'].find_one({'_id': _id,'is_deleted': False}, {"is_deleted": 0})
                    
                    if data is None:
                        return JsonResponse(output_format(message='Address not found.'))
                    else: 
                        return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Address not fetched.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))

##### for updating customer address
    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='address id not received.'))
            
            # if id is receivied
            else:
                address = database['Ship-add'].find_one({'_id': _id})
                if address is None:
                    return JsonResponse(output_format(message='Address not found.'))
                try:
                    
                    data = request.data.dict()
                    if data.get('pincode') is not None:
                        data['pincode'] = int(data['pincode'])
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                try:
                    result = database['Ship-add'].update_one(filter={'_id': _id}, update= {"$set":data})
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Update failed.'))

##### for deleting customer address using address_id
    elif request.method == 'DELETE':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:

            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Address id not received.'))
            else:
                address = database['Ship-add'].find_one({'_id': _id,'user_id': user['_id'], "is_deleted": False})
                if address is None:
                    return JsonResponse(output_format(message='Address not found.'))

                result = database['Ship-add'].update_one(filter={'_id':_id}, update={'$set': {'is_deleted': True}})
                if result.modified_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Delete failed.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))



@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
def product_discount(request, _id=None):

##### for adding discount from admin panel
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            request_data = request.data.dict()
            data = {}
            #checking if cat_type already exists
            if database['Discount'].find_one({'coupon_code': request_data['coupon_code'], 'is_deleted': False}) is None:
                print(request_data)
                #checking data format
                try:
                    data['disc_percent'] =  float(request_data['disc_percent'])
                    data['coupon_code'] = request_data['coupon_code']   
                    data['min_ord_val'] = float(request_data['min_ord_val'])
                    data['valid_from'] = datetime.datetime.strptime(request_data['valid_from'], '%Y-%m-%dT%H:%M:%S.%fZ')   #date
                    data['valid_until'] = datetime.datetime.strptime(request_data['valid_until'], '%Y-%m-%dT%H:%M:%S.%fZ')   #date
                    data['max_disc_amt'] = float(request_data['max_disc_amt'])
                    data['create_date'] = datetime.datetime.now()
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))

                #inserting data
                try:
                    data['_id'] = create_unique_object_id()
                    data['is_deleted'] = False
                    database['Discount'].insert_one(data)
                    return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Discount not inserted.'))
            else:
                return JsonResponse(output_format(message='Coupon code already exists.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

##### get coupon codes into admin panel
    elif request.method == 'GET':

        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            # checking for path parameters
            if _id == None:

                #getting and returning all the suppliers from the db
                try:
                    data = database['Discount'].find({'is_deleted': False}, {"is_deleted": 0})
                    data = [i for i in data]
                    print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Discounts not fetched.'))
            
            # path parameter available
            else:
                try:
                    data=database['Discount'].find_one({'_id': _id, 'is_deleted': False}, {"is_deleted": 0})
                    
                    if data is None:
                        return JsonResponse(output_format(message='Discount not found.'))
                    else: 
                        return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Discount not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


    elif request.method == 'PATCH':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Discount id not received.'))
            
            else:
                try:
                    request_data = request.data.dict()
                    data = {}
                    data['disc_percent'] =  float(request_data['disc_percent'])
                    data['coupon_code'] = request_data['coupon_code']   
                    data['min_ord_val'] = float(request_data['min_ord_val'])
                    data['valid_from'] = datetime.datetime.strptime(request_data['valid_from'], '%Y-%m-%dT%H:%M:%S.%fZ')   #date
                    data['valid_until'] = datetime.datetime.strptime(request_data['valid_until'], '%Y-%m-%dT%H:%M:%S.%fZ')   #date
                    data['max_disc_amt'] = float(request_data['max_disc_amt'])
                except: 
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                discount = database['Discount'].find_one(filter={'_id': _id, 'is_deleted': False})
                
                if discount is None:
                    return JsonResponse(output_format(message='Discount not found.'))
                else:
                
                    result = database['Discount'].update_one(filter={'_id': _id, 'is_deleted': False},
                                                                        update={'$set': data})
                    print(dir(result))
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                    else:
                        return JsonResponse(output_format(message='Update failed!'))



    elif request.method == 'DELETE':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Discount id not received.'))
            else:
                discount = database['Discount'].find_one({'_id': _id, "is_deleted": False})

                if discount is None:
                    return JsonResponse(output_format(message='Discount not found.'))
                else:
                    result = database['Discount'].update_one({'_id': _id, 'is_deleted': False},
                                                             {'$set' : {'is_deleted' : True}})
                    
                    if result.modified_count == 1:
                        return JsonResponse(output_format(message='Success!'))
                    else:
                        return JsonResponse(output_format(message='Delete failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


                
          
                
    

@api_view(['POST'])
def check_discount_code(request):

##### for checking coupon codes on checkout page
    if request.method == 'POST':

        #fetching customer details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            request_data = request.data.dict()
            
            discount = database['Discount'].find_one({'coupon_code': request_data['coupon_code'], "is_deleted": False}, {"is_deleted": 0})

            if discount is None:
                return JsonResponse(output_format(message='Wrong coupon code.'))

############ errrorororororororororos hererererererwdsfwdsferdsfwed
            if discount['valid_until'] < datetime.datetime.today():
                return JsonResponse(output_format(message='Coupon code expired.'))
            
            data = {}
            total_amount = float(request_data['total_amount'])
            print(total_amount)
            if total_amount > discount['min_ord_val'] :
                print(discount['disc_percent'])
                
                discount_percent = discount['disc_percent'] * 0.01
                appied_disc = total_amount * discount_percent
                
            if appied_disc > discount['max_disc_amt']:
                data['applied_disc'] = discount['max_disc_amt']
            else:
                data['applied_disc'] = appied_disc
                data['_id'] = discount['_id']
                data['disc_percent'] = discount['disc_percent']
            
            data['applied_disc'] = int(data['applied_disc'])

            #sending calculated data
            return JsonResponse(output_format(message='Success!', data=data))
        else:
            return JsonResponse(output_format(message='User not customer.'))

@api_view(['POST', 'GET'])
def customer_order(request):
##### place an order by customer
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            try:
                data = json.loads(request.body)     #loading body string to json data
                print(data)
            except:
                return JsonResponse(output_format(message='Wrong data format.'))

            #checking whether address exists
            order_address = database['Ship-add'].find_one(filter={'_id':data['add_id'], 'user_id':user['_id']})
            if order_address is None:
                    return JsonResponse(JsonResponse(output_format(message='Address doesn\'t exist.')))

            #checking whether coupon code exists
            try:
                if data.get('disc_id'):
                    order_discount = database['Discount'].find_one(filter={'_id': data['disc_id']})
                    if order_discount is None:
                        return JsonResponse(output_format(message='Wrong coupon code.'))
            except:
                pass

            # performing product related checks(if product exists, size available?, 
            # qty available?, out of stock or not.)
            
            data['Order-details'] = convert_structure(data['Order-details'])
            
            for ordered_product in data['Order-details']:

                product = database['Product'].find_one(
                    filter={'_id': ordered_product['prod_id']})     #fetching product from product table

                #checking whether product exists
                if product is None:
                    return JsonResponse(output_format(message='Product doesn\'t exist.'))

                for size, qty in ordered_product['prod_qty'].items():       #looping data from POST request
                    available_qty = product['prod_qty'].get(size)
                    pass
                    if qty < 1:
                        return JsonResponse(output_format(message='Invalid quantity.', data={'prod_id': product['_id']}))
                    #checking size availability
                    if available_qty is None:
                        return JsonResponse(output_format(message='Selected size not available.'))

                    #checking stock availability
                    if available_qty >= qty:
                        database['Product'].update_one(
                            {'_id': product['_id']}, {'$set': {f'prod_qty.{size}': available_qty-qty}}
                        )       #updating product qty
                    
                    # if stock is 0 return 'out of stock'
                    elif available_qty == 0:
                        return JsonResponse(output_format(message='Product out of stock.',data={'prod_id': product['_id']}))
                    # received qty is more than available qty
                    else:
                        return JsonResponse(output_format(message='Entered more quantity then available.', data={'prod_id': product['_id'], 'available_qty': available_qty}))

            data['order_date'] = datetime.datetime.now()
            data['user_id'] = user['_id']
            data['order_status'] = 'Failed'
            
            
            # authorize razorpay client with API Keys.
            client = razorpay.Client(auth=(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']), 
                                                    base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_SECRET'])))


            # creating order to send in response
            try:
                razorpay_order = client.order.create({
                                'amount':100*(data['total_amount']-data['discount']), 'currency': 'INR',
                                'payment_capture': '1'})

                #inserting data
                try:
                    order_id = create_unique_object_id()
                    data['_id'] = order_id
                    database['Order'].insert_one(data)
                    # return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Order not inserted.'))
                
                if razorpay_order is not None:
                    
                    response_data={}
                    
                    response_data['razorpay_order_id'] = razorpay_order['id']
                    response_data['name'] = user['name']
                    response_data['order_amount'] = (data['total_amount']-data['discount'])
                    response_data['currency'] = 'INR'
                    response_data['merchantId'] = base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID'])
                    response_data['order_id'] = order_id
                    
                
                    return JsonResponse(output_format(message='Success!', data=response_data))
            except:
                return JsonResponse(output_format(message='Razorpay error.'))
            
        else:
            return JsonResponse(output_format(message='User not customer.'))

    ##### get all orders as a customer
    elif request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:

            #getting and returning all the products from the db
            try:
                
                # query to get all customer orders
                data = database['Order'].aggregate([
                    { '$match': { 'user_id': user['_id'] } },
                    { '$unwind': "$Order-details" },
                    {
                        '$project': {
                        'prod_id': "$Order-details.prod_id",
                        'prod_qty': { '$objectToArray': "$Order-details.prod_qty" },
                        'add_id': 1,
                        'disc_id': 1,
                        'order_status': 1,
                        'total_amount':1,
                        'discount':1,
                        '_id': 1,
                        'order_date':1
                        },
                    },
                    { '$unwind': "$prod_qty" },
                    {
                        '$project': {
                        '_id': "$_id",
                        'prod_id': "$prod_id",
                        'size': "$prod_qty.k",
                        'qty': "$prod_qty.v",
                        'add_id': 1,
                        'disc_id': 1,
                        'order_status': 1,
                        '_id': 1,
                        'total_amount':1,
                        'discount':1,
                        'order_date':1
                        },
                    },
                    {
                        '$lookup': {
                        'from': "Product",
                        'localField': "prod_id",
                        'foreignField': "_id",
                        'as': "Product",
                        },
                    },
                    { '$unwind': "$Product" },
                    {
                        '$project': {
                        'add_id': 1,
                        'disc_id': 1,
                        'order_status': 1,
                        'total_amount':1,
                        'discount':1,
                        '_id': 1,
                        'order_date':1,
                        'prod_id': "$prod_id",
                        'size': "$size",
                        'prod_image': { '$arrayElemAt': ["$Product.prod_image", 0] },
                        'qty': "$qty",
                        'prod_name': "$Product.prod_name",
                        'prod_price': "$Product.prod_price",
                        },
                    },
                    {
                        '$group': {
                        '_id': {
                            '_id': "$_id",
                            'add_id': "$add_id",
                            'disc_id': "$disc_id",
                            'order_status': "$order_status",
                            'total_amount': '$total_amount',
                            'discount': '$discount',
                            'order_date':'$order_date'
                        },
                        'Order_details': {
                            '$push': {
                            'prod_name': "$prod_name",
                            'size': "$size",
                            'qty': "$qty",
                            'prod_image': "$prod_image",
                            'prod_id': "$prod_id",
                            'prod_price': "$prod_price",
                            },
                        },
                        },
                    },
                    {
                        '$lookup': {
                        'from': "Ship-add",
                        'localField': "_id.add_id",
                        'foreignField': "_id",
                        'as': "Ship-add",
                        },
                    },
                    { '$unwind': "$Ship-add" },
                    {
                        '$project': {
                        '_id': "$_id._id",
                        'add_id': "$_id.add_id",
                        'total_amount':"$_id.total_amount",
                        'discount':"$_id.discount",
                        'house_no': "$Ship-add.house_no",
                        'area_street': "$Ship-add.area_street",
                        'add_type': "$Ship-add.add_type",
                        'pincode': "$Ship-add.pincode",
                        'state': "$Ship-add.state",
                        'city': "$Ship-add.city",
                        'order_status': "$_id.order_status",
                        'order_date': '$_id.order_date',
                        "Order_details": "$Order_details",     
                        },
                    },
                    { '$sort': { 'order_date': -1 } }
                    ])
           
                data = list(data)
        
                if not data:
                    return JsonResponse(output_format(message='Orders not found.'))
                else:
                    return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Orders not fetched.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))

@api_view(['GET'])
def order_invoice(request, _id=None):
    
    if request.method == 'GET':

        #fetching customer details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            # checking for path parameters
            if _id == None:
                return JsonResponse(output_format(message='Order id not received.'))
            else:
                
                data = database["Order"].aggregate([
                        {
                            "$match": {
                                "user_id": user['_id'],
                                "_id": _id
                            }
                        },
                        {"$unwind": "$Order-details"},
                        {
                            "$project": {
                                "prod_id": "$Order-details.prod_id",
                                "prod_qty": {
                                    "$objectToArray": "$Order-details.prod_qty"
                                },
                                "add_id": 1,
                                "total_amount": 1,
                                "discount": 1,
                                "_id": 1,
                                "order_date": 1,
                                "Payment-details": 1
                            }
                        },
                        {"$unwind": "$prod_qty"},
                        {
                            "$project": {
                                "_id": 1,
                                "prod_id": "$prod_id",
                                "size": "$prod_qty.k",
                                "qty": "$prod_qty.v",
                                "add_id": 1,
                                "disc_id": 1,
                                "total_amount": 1,
                                "discount": 1,
                                "order_date": 1,
                                "Payment-details": 1
                            }
                        },
                        {
                            "$lookup": {
                                "from": "Product",
                                "localField": "prod_id",
                                "foreignField": "_id",
                                "as": "Product"
                            }
                        },
                        {"$unwind": "$Product"},
                        {
                            "$project": {
                                "add_id": 1,
                                "total_amount": 1,
                                "discount": 1,
                                "_id": 1,
                                "order_date": 1,
                                "Payment-details": 1,
                                "size": "$size",
                                "qty": "$qty",
                                "prod_name": "$Product.prod_name",
                                "prod_price": "$Product.prod_price",
                                'prod_desc': '$Product.prod_desc'
                            }
                        },
                        {
                            "$group": {
                                "_id": {
                                    "_id": "$_id",
                                    "add_id": "$add_id",
                                    "total_amount": "$total_amount",
                                    "discount": "$discount",
                                    "order_date": "$order_date",
                                    "Payment-details": "$Payment-details"
                                },
                                "Order_details": {
                                    "$push": {
                                        "prod_name": "$prod_name",
                                        "size": "$size",
                                        "qty": "$qty",
                                        "prod_price": "$prod_price",
                                        'prod_disc': '$prod_desc'
                                    }
                                }
                            }
                        },
                        {
                            "$lookup": {
                                "from": "Ship-add",
                                "localField": "_id.add_id",
                                "foreignField": "_id",
                                "as": "Ship-add"
                            }
                        },
                        {"$unwind": "$Ship-add"},
                        {
                            "$project": {
                                "_id": "$_id._id",
                                "add_id": "$_id.add_id",
                                "total_amount": "$_id.total_amount",
                                "discount": "$_id.discount",
                                "house_no": "$Ship-add.house_no",
                                "user_id": "$Ship-add.user_id",
                                "area_street": "$Ship-add.area_street",
                                "add_type": "$Ship-add.add_type",
                                "pincode": "$Ship-add.pincode",
                                "state": "$Ship-add.state",
                                "city": "$Ship-add.city",
                                "Payment-details": "$_id.Payment-details",
                                "order_date": "$_id.order_date",
                                "Order_details": "$Order_details"
                            }
                        },
                        {
                            "$lookup": {
                                "from": "User",
                                "localField": "user_id",
                                "foreignField": "_id",
                                "as": "User"
                            }
                        },
                        {"$unwind": "$User"},
                        {
                            "$project": {
                                "_id": "$_id",
                                "total_amount": "$total_amount",
                                "discount": "$discount",
                                "house_no": "$house_no",
                                "area_street": "$area_street",
                                "add_type": "$add_type",
                                "pincode": "$pincode",
                                "state": "$state",
                                "city": "$city",
                                "razorpay_payment_id": "$Payment-details.razorpay_payment_id",
                                "order_date": "$order_date",
                                "Order_details": 1,
                                "email": "$User.email",
                                "name": "$User.name",
                                "mobile_no": "$User.mobile_no"
                            }
                        }
                    ])
                
                try:
                    data = data.next()
                except:
                    return JsonResponse(output_format(message='Order not fetched.'))
                
                client = razorpay.Client(auth=(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']), 
                                                            base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_SECRET'])))

                output = client.payment.fetch(data['razorpay_payment_id'])
                payment_method = output.get('method')
                if payment_method == 'card':
                    data['card_last4'] = output['card']['last4']
                elif payment_method == 'upi':
                    data['card_last4'] = output['upi_transaction_id']
                    
                data.pop('razorpay_payment_id')
                return JsonResponse(output_format(message='Success!', data=data))
        else:
            return JsonResponse(output_format(message='User not customer.'))

            
        

@api_view(['POST'])
def verify_order(request):
    
    if request.method == 'POST':
        
        #fetching customer details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            # getting data form request
            if request.data.get('response1'):
                response = request.data['response1']


                client = razorpay.Client(auth=(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']), 
                                                            base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_SECRET'])))
                if "razorpay_signature" in response:

                    # Verifying Payment Signature
                    # is_sign_valid = client.utility.verify_payment_signature(response)

                    
                    # checking if we get here True signature 
                    if client.utility.verify_payment_signature(response):
                        
                        payment_details = {
                                'razorpay_order_id': response['razorpay_order_id'],
                                'razorpay_payment_id': response['razorpay_payment_id'],
                                'razorpay_signature': response['razorpay_signature']
                                }
                        
                        result = database['Order'].update_one({'_id': response['order_id']}, 
                                                    {'$set': {'order_status': 'Pending', 
                                                            'Payment-details': payment_details}})
                        
                        database['Cart'].delete_one({'_id':user['_id']})

                        if result.modified_count == 1:
                            return JsonResponse(output_format(message='Success!'))

            # Handling failed payments
            elif request.data.get('dataError'):

                response = request.data['dataError']
                
                order = database['Order'].find_one({'_id': response['ord_id']})
                for ordered_product in order['Order-details']:

                    product = database['Product'].find_one(
                        filter={'_id': ordered_product['prod_id']})     #fetching product from product table

                

                    for size, qty in ordered_product['prod_qty'].items():       #looping data from POST request
                        available_qty = product['prod_qty'].get(size)

                        database['Product'].update_one(
                            {'_id': product['_id']}, {'$inc': {f'prod_qty.{size}': qty}}
                        )       #updating product qty

                    return JsonResponse(output_format(message='Order failed.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))


# @api_view(['POST', 'GET'])
# def add_to_cart(request):

# ##### adding products to cart
#     if request.method == 'POST':

#         #fetching customer details
#         user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
#         #checking if user is admin
#         if user['role'] == 'customer' and user['_id'] == request.id:


#             try:
#                 data = json.loads(request.body)     #loading body string to json data
#             except:
#                 return JsonResponse(output_format(message='Wrong data format.'))

#         for added_product in data['Cart-details']:

#             product = database['Product'].find_one(filter={'_id': added_product['prod_id']})
            
#             if product is None:
#                 return JsonResponse(output_format(message='Product doesn\'t exist.'))
#             cart_qty = {}
#             for size, qty in added_product['prod_qty'].items():
            
#                 available_qty = product['prod_qty'].get(size)
#                 if qty < 1:
#                     return JsonResponse(output_format(message='Invalid quantity.', data={'prod_id': product['_id']}))
#                 #checking size availability
#                 if available_qty is None:
#                     return JsonResponse(output_format(message='Selected size not available.'))

#                 # if stock is 0 return 'out of stock'
#                 if available_qty == 0:
#                     return JsonResponse(output_format(message='Product out of stock.',data={'prod_id': product['_id']}))
#                 #checking stock availability
#                 elif available_qty < qty:
#                     return JsonResponse(output_format(message='Entered more quantity then available.', data={'prod_id': product['_id'], 'available_qty': available_qty}))
#                 # received qty is more than available qty
#                 else:
#                     # cart_qty[f'Cart-detailsprod_qty.{size}'] = qty
#                     continue

#         user_cart = database['Cart'].find_one({'user_id': user['_id']})
#         print(cart_qty)
#         database['Cart']['Cart-details'].update_one({"_id": user['_id']},
#             {"$inc": {'total_amount': data['total_amount'], 'Cart-details': data['Cart-details']}}
#         )
               

@api_view(['POST', 'GET'])
def add_to_cart(request):

##### adding products to cart
    if request.method == 'POST':

        #fetching customer details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:
            try:
                data = json.loads(request.body)     #loading body string to json data
            except:
                return JsonResponse(output_format(message='Wrong data format.'))

            product = database['Product'].find_one({'_id': data['prod_id']})

            if product is None:
                return JsonResponse(output_format(message='Product not found.'))
            

            for size, qty in data['prod_qty'].items():
                available_qty = product['prod_qty'].get(size)
                pass

                if qty < 1:
                    return JsonResponse(output_format(message='Invalid quantity.', data={'prod_id': product['_id']}))
                #checking size availability
                if available_qty is None:
                    return JsonResponse(output_format(message='Selected size not available.'))

                #checking stock availability
                if available_qty >= qty:
                    # database['Product'].update_one(
                    #     {'_id': product['_id']}, {'$set': {f'prod_qty.{size}': available_qty-qty}}
                    # )       #updating product qty
                    existing_product = database['Cart'].find_one({'user_id': user['_id'], 'prod_id': product['_id']})


                    ######## here i'm checking the total amount in new updated cart
                    if existing_product is not None:
                        database['Cart'].update_one({"user_id": user['_id'], "prod_id": product['_id']},
                                {"$inc": {f'prod_qty.{size}': qty}}
                            )
                        return JsonResponse(output_format(message='Success!'))
                    else:
                        data['_id'] = create_unique_object_id()
                        data['user_id'] = user['_id']
                        database['Cart'].insert_one(data)
                        return JsonResponse(output_format(message='Success!'))

                
                # if stock is 0 return 'out of stock'
                elif available_qty == 0:
                    return JsonResponse(output_format(message='Product out of stock.',data={'prod_id': product['_id']}))
                # received qty is more than available qty
                else:
                    return JsonResponse(output_format(message='Entered more quantity then available.', data={'prod_id': product['_id'], 'available_qty': available_qty}))

        # # data['_id'] = user['_id']
        # data['total_amount'] += user_cart['total_amount']
        # if user_cart is None:
        #     data['_id'] = user['_id']
        #     data['Cart-details'] = {'prod_id': data['prod_id'], 'prod_qty':data['prod_qty']}

        #     try:
        #         database['Cart'].insert_one(data)
        #     except:
        #         return JsonResponse(output_format(message='Product not inserted.'))
        
        # else:
        #     database['Product'].update_one({"_id": user['prod_id']},
        #             {"$inc": prod_qty}
        #         )
            














# quewrty params
    # pass
    # print(request.query_params)
    # print(json.dumps(request.query_params))
    # pass

@api_view(['POST'])
def request_password_reset(request):

##### Forgot password feature for users
    if request.method == 'POST':
        
        data = request.data
        
        email = data.get('email')
        if email is not None:

            #fetching user details
            user = database['User'].find_one(filter={'email':email})
            #checking if user
            if user is None:
                return JsonResponse(output_format(message='User doesn\'t exist.'))
            

            token = jwt.encode({'id': {'id':user['_id'],'role':user['role']},
                        'exp': datetime.datetime.now() + datetime.timedelta(
                            days=1)},
                        jwt_secret, algorithm='HS256')
            encoded_token = base64.b64encode(token.encode('ascii'))
            # encoded_token = base64.b64encode(token)
            print(token)
            print(encoded_token.decode())

            try:
                reset_url = f"localhost:3000/resetpassword/{encoded_token.decode()}/"
                body = f'''<body style="font-family:system-ui;font-size:15px;"><h2 style="color: black;">Trouble signing in?</h2><p style="color: black;">Hey, Resetting your password is easy.</p><p style="color: black;">Copy & paste this link into your browser and follow the instructions. We'll have you up and
                running in no time.</p><p style="color:darkblue;word-wrap:break-word;text-decoration:underline;">{reset_url}</p><p style="color: black;">If you did not make this request then please ignore this email.</p></body>
                    '''
                subject = 'Reset your password'
                recipients=[user['email']]
                
                send_email(subject=subject, body=body, recipients=recipients)
                return JsonResponse(output_format(message='Success!'))
            except:
                return JsonResponse(output_format(message='Failed to send password reset mail.'))

@api_view(['GET', 'POST'])
def reset_password(request):

##### reseting new password sent by user  
    if request.method == 'POST':
        
        data = request.data
        new_password = data.get('newPassword')
        if new_password is not None:
            #fetching user details
            user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
            #checking if user is admin
            if user['role'] == request.role and user['_id'] == request.id:
                database['User'].update_one({'email': user['email']}, {'$set': {'password': pwd_context.hash(new_password)}})
            
                return JsonResponse(output_format(message='Success!'))
            
            else:
                return JsonResponse(output_format(message='User not found.'))
        
        else:
            return JsonResponse(output_format(message='New password not found.'))
    
    elif request.method == 'GET':
        # fetching user
        user = database['User'].find_one({'_id' : request.id, 'role': request.role})
        
        #checking if user is admin
        if user['role'] == request.role and user['_id'] == request.id:
            return JsonResponse(output_format(message='User exists.'))
        else:
            return JsonResponse(output_format(message='User doesn\'t exist.'))
        

@api_view(['GET'])
def customer_product(request, _id=None):

    if request.method == 'GET':
        
        if _id == None:

                try:

                    # Aggregate for getting all products to customer side
                    data = database['Category-type'].aggregate([
                            {
                            "$lookup":
                                {
                                    "from": "Category",
                                    "localField": "_id",
                                    "foreignField": "cat_type_id",
                                    "as": "Category"
                                }
                            },
                            {
                                "$unwind": "$Category"
                            },
                            {
                            "$lookup":
                                {
                                    "from": "Product",
                                    "localField": "Category._id",
                                    "foreignField": "cat_id",
                                    "as": "Product"
                                }
                            },
                            {
                            "$unwind": "$Product"
                            },
                            {
                                "$match": {'Category.active': True, 'Product.active': True, 'active': True,
                                           'Category.is_deleted': False, 'Product.is_deleted': False, 'is_deleted': False}
                            },
                            {
                                '$lookup': {
                                'from': "Rating",
                                'let': { 'prod_id': "$Product._id" },
                                'pipeline': [
                                    { '$match': { '$expr': { '$eq': ["$prod_id", "$$prod_id"] } } },
                                    { '$group': { '_id': "$prod_id", 'rating': { '$avg': "$rating" }, 'user_count': { '$sum': 1 } } },
                                    { '$project': { '_id': 0 } }
                                ],
                                'as': "Rating"
                                }
                            },
                            {
                                "$project":
                                {
                                    'rating': { '$ifNull': [{ '$arrayElemAt': ["$Rating.rating", 0] }, None] },
                                    'user_count': { '$ifNull': [{ '$arrayElemAt': ["$Rating.user_count", 0] }, 0] },
                                    "_id": "$Product._id",
                                    "prod_name": "$Product.prod_name",
                                    "prod_desc": "$Product.prod_desc",
                                    "prod_image": {"$arrayElemAt": ["$Product.prod_image", 0]},
                                    # "prod_image": {"$slice": ["$Product.prod_image", 2]},
                                    "prod_price": "$Product.prod_price",
                                    "cat_id" : "$Product.cat_id",
                                    "cat_title": "$Category.cat_title",
                                    "cat_type_id": "$Category.cat_type_id",
                                    "cat_type": "$cat_type",
                                    
                                }
                            }])
                    data = list(data)
                    print(data[0])
                    #shuffling the data using random module's shuffle
                    random.shuffle(data)
                    # print(data)
                    return JsonResponse(output_format(message='Success!', data=data))
                except:
                    return JsonResponse(output_format(message='Products not fetched.'))
        # single product data fetch            
        else:
            try:
                # data = database['Product'].find_one(filter={"_id": _id,'is_deleted': False, 'active': True}, 
                #                                 projection={'is_deleted':0, 'active':0})
                data = database["Product"].aggregate([
                            {
                                '$match': {"_id": _id,'is_deleted': False, 'active': True}
                            },
                            {
                                '$lookup': {
                                'from': "Rating",
                                'let': { 'prod_id': "$_id" },
                                'pipeline': [
                                    { '$match': { '$expr': { '$eq': ["$prod_id", "$$prod_id"] } } },
                                    { '$group': { '_id': "$prod_id", 'rating': { '$avg': "$rating" }, 'user_count': { '$sum': 1 } } },
                                    { '$project': { '_id': 0 } }
                                ],
                                'as': "Rating"
                                }
                            },
                            {
                                '$project': {
                                'rating': { '$ifNull': [{ '$arrayElemAt': ["$Rating.rating", 0] }, None] },
                                'user_count': { '$ifNull': [{ '$arrayElemAt': ["$Rating.user_count", 0] }, 0] },
                                'prod_name': 1,
                                'cat_id': 1,
                                'prod_price': 1,
                                'prod_desc':1,
                                'prod_image': 1,
                                'created_at': 1,
                                'prod_qty': {'$arrayToObject': {
                                                '$filter': {
                                                'input': { '$objectToArray': "$Product.prod_qty" },
                                                'as': "item",
                                                'cond': { '$ne': [ "$$item.v", 0 ] }
                                                }
                                            }}
                                }
                            }
                            ])


                if data is not None:
                    return JsonResponse(output_format(message='Success!', data=data)) 
                else:
                    return JsonResponse(output_format(message='Product not found!'))
            except:
                return JsonResponse(output_format(message='Product not fetched.'))
            #     data = out.next()
            #     return JsonResponse(output_format(message='Success!', data=data))
            # except:
            #     return JsonResponse(output_format(message='Product not fetched.'))
            

            # send_email()
            # print(reset_url)
            # return JsonResponse(output_format(message='Success!', data={'reset_url': reset_url}))
            # # f"Hello {'Raj'},\n Here is a link to reset the password for Gurukrupa Fashion Shopping Site which expires in 2 hours.\n\n\t\t{'localhost\:3000/forgot-passoword/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6eyJpZCI6IklELTY2MmY4NjFiLTZmMWQtNGMwNy05OWY0LWEwMTEzMWJmZWYzOSIsInJvbGUiOiJhZG1pbiJ9LCJleHAiOjE2NzUwMTY4NjF9.VmhDp1LnYJ2PBNaXqMP-cFmBpndxLsHSTRd8Tczzqr8/'}\nHave a nice day ahead."





@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
def cart(request):
    if request.method == 'POST':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            try:
                data = json.loads(request.body)     #loading body string to json data
                prod_id = data['prod_id']
                # size, qty = data['prod_qty'].items()
                size, qty = list(data['prod_qty'].keys())[0], list(data['prod_qty'].values())[0]
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
            
            #checking if product exists or not
            if database['Product'].find_one({'_id': prod_id, 'is_deleted': False, 'active': True}) is None:
                return JsonResponse(output_format(message='Product doesn\'t exist.'))
            
            # checking if given already exists in cart
            product_exist = database['Cart'].find_one({'_id': user['_id'], "Cart-details.prod_id": prod_id})
            
            #product not available in Cart
            if product_exist is None:
                
                if database['Cart'].find_one({'_id': user['_id']}) is None:
                    database['Cart'].insert_one(document={'_id': user['_id'], 
                                                          'Cart-details': [{
                                                              'prod_id': prod_id,
                                                                'prod_qty': {
                                                                    size: qty
                                                                }
                                                          }]})
                    return JsonResponse(output_format(message='Success!'))
                
                
                result = database['Cart'].update_one({'_id': user['_id']}, {'$push': {
                                        "Cart-details" : {
                                            "prod_id" : prod_id,
                                            "prod_qty" : {
                                                size: qty
                                            }
                                        }}})
                if result.modified_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Product not added to cart.'))
            
            #product already available in Cart
            else:
                
                result = database['Cart'].update_one({'_id': user['_id'], "Cart-details.prod_id": prod_id}, 
                                        {'$inc': {f'Cart-details.$.prod_qty.{size}': qty}})
                
                if result.modified_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Product not added to cart.'))
                
            
            # return JsonResponse(output_format(data = [prod_id, size, qty]))
        
        else:
            return JsonResponse(output_format(message='User not customer.'))

    elif request.method == 'GET':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:

                try:

                    # Aggregate for getting all products to customer side
                    
                    data = database["Cart"].aggregate([
                                {'$match': {"_id": user['_id']}},
                                { '$unwind': "$Cart-details" },
                                {
                                    '$project': {
                                    'prod_id': "$Cart-details.prod_id",
                                    'prod_qty': { '$objectToArray': "$Cart-details.prod_qty" },
                                    }},
                                { '$unwind': "$prod_qty" },
                                {
                                    '$project': {
                                    '_id' : "$_id",
                                    'prod_id': "$prod_id",
                                    'size': "$prod_qty.k",
                                    'qty': "$prod_qty.v",
                                    }},
                                {
                                    '$lookup':{
                                    'from' : "Product",
                                    'localField': "prod_id",
                                    'foreignField': "_id",
                                    'as': "Product"
                                    }},
                                {'$unwind': "$Product"},
                                {
                                    '$project':{
                                    "size": "$size",
                                    "qty": "$qty",
                                    "prod_id": "$prod_id",
                                    "prod_name": "$Product.prod_name",
                                    "prod_image": {"$arrayElemAt": ["$Product.prod_image", 0]},
                                    "prod_price": "$Product.prod_price",
                                    "cat_title": "$Category.cat_title",
                                    "cat_id" : "$Product.cat_id",
                                    }}
                                ])

                    data = [i for i in data]
                    
                    if data:
                        print(data)
                        return JsonResponse(output_format(message='Success!', data=data))
                    else:
                        return JsonResponse(output_format(message='Cart is empty.'))
                except:
                    return JsonResponse(output_format(message='Products not fetched.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))        
      
    elif request.method == 'PATCH':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            try:
                data = json.loads(request.body)     #loading body string to json data
                prod_id = data['prod_id']
                size, qty = list(data['prod_qty'].keys())[0], list(data['prod_qty'].values())[0]
  
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
            
            #checking if product exists or not
            if database['Product'].find_one({'_id': prod_id, 'is_deleted': False, 'active': True}) is None:
                return JsonResponse(output_format(message='Product doesn\'t exist.'))
            
            # checking if given already exists in cart
            product_exist = database['Cart'].find_one({'_id': user['_id'], "Cart-details.prod_id": prod_id})
            
            #product not available in Cart
            if product_exist is None:
                return JsonResponse(output_format(message='Product doesn\'t exist in cart.'))
                
            #product already available in Cart
            else:
                print({f'Cart-details.$.prod_qty.{size}': qty})
                result = database['Cart'].update_one({'_id': user['_id'], "Cart-details.prod_id": prod_id}, 
                                        {'$set': {f'Cart-details.$.prod_qty.{size}': qty}})
                
                if result.modified_count == 1 or result.matched_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Product not added to cart.'))
                
        else:
            return JsonResponse(output_format(message='User not customer.'))

    elif request.method == 'DELETE':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            #if request's body is blank then it will delete(clear) whole cart 
            if request.body:
                try:
                    data = json.loads(request.body)     #loading body string to json data
                    prod_id = data['prod_id']
                    size, qty = list(data['prod_qty'].keys())[0], list(data['prod_qty'].values())[0]

                except:
                    return JsonResponse(output_format(message='Wrong data format.'))

                result = database["Cart"].aggregate([
                        {'$match': {'_id': user['_id']}},
                        { '$unwind': "$Cart-details" },
                        {
                            '$project': {
                            '_id': 0,
                            'prod_id': "$Cart-details.prod_id",
                            'prod_qty': { '$objectToArray': "$Cart-details.prod_qty" },
                            },
                        },
                        {'$match': { 'prod_id': prod_id}},
                        {
                            '$project': {
                            'prod_id': "$prod_id",
                            'len_of_size': {'$size': "$prod_qty.k"},
                            'size': '$prod_qty.k'
                            }}
                        ])
                try:
                    result = list(result)[0]
                    print(result['size'], result['prod_id'])
                    print(size in result['size'])
                    
                    #if there is only one size in cart for same product
                    if result['len_of_size'] == 1 and size in result['size'] and result['prod_id'] == prod_id:
                        update_result = database['Cart'].update_one(filter={"_id": user['_id']}, 
                                update={'$pull': { "Cart-details": { "prod_id": prod_id} } })
                        
                        if update_result.modified_count == 1:
                            return JsonResponse(output_format(message='Success!'))

                    #if received size in not available in cart
                    elif size not in result['size']:
                        return JsonResponse(output_format(message='Given size doen\'t exist in cart.'))
                    
                    #if there is more than one size in cart for same product
                    else:
                        database['Cart'].update_one({'_id': user['_id'],  "Cart-details.prod_id": prod_id },
                            { '$unset': { f"Cart-details.$.prod_qty.{size}": "" } })
                        return JsonResponse(output_format(message='Success!'))
                except:
                    return JsonResponse(output_format(message='Deleted failed.'))

            #clearing the whole cart
            else:
                out = database['Cart'].delete_one(filter={'_id': user['_id']})
                if out.deleted_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Deleted failed.'))
                
        else:
            return JsonResponse(output_format(message='User not customer.'))

@api_view(['GET'])
def cart_count(request):
    if request.method == 'GET':
        #fetching user details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            data = database["Cart"].aggregate([
                                {'$match': {"_id": user['_id']}},
                                { '$unwind': "$Cart-details" },
                                {
                                    '$project': {
                                    'prod_id': "$Cart-details.prod_id",
                                    'prod_qty': { '$objectToArray': "$Cart-details.prod_qty" },
                                    }},
                                { '$unwind': "$prod_qty" },
                                {
                                    '$project': {
                                    '_id' : "$_id",
                                    'prod_id': "$prod_id",
                                    'size': "$prod_qty.k",
                                    'qty': "$prod_qty.v",
                                    }},
                                {
                                    '$project':{
                                    'prod_id': "$prod_id"
                                    }},
                                        {
                                          '$count': "cart_count"
                                        }
                                ])
            data = [i for i in data]
            print(data)
            if data:
                print(data)
                return JsonResponse(output_format(message='Success!', data=data[0]))
            else:
                return JsonResponse(output_format(message='Success!', data={'cart_count':0}))
    else:
        return JsonResponse(output_format(message='User not customer.'))

    
@api_view(['POST'])
def get_payment(request):

    if request.method == 'POST':
        #fetching user details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            try:
                rec_data = request.data.dict()     #loading body string to json data
                order_amount = float(rec_data['order_amount'])
                
                
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
            
            
            # authorize razorpay client with API Keys.
            client = razorpay.Client(auth=(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']), 
                                                    base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_SECRET'])))

            # creating order to send in response
            try:
                razorpay_order = client.order.create({
                                'amount':100*order_amount, 'currency': 'INR',
                                'payment_capture': '0'})
                
                if razorpay_order is not None:
                    data={}
                    
                    data['razorpay_order_id'] = razorpay_order['id']
                    data['name'] = user['name']
                    data['order_amount'] = order_amount
                    data['currency'] = 'INR'
                    data['merchantId'] = base64decode(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']))
                
                    return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Razorpay error.'))
        else:
            return JsonResponse(output_format(message='User not customer.'))


@api_view(['POST'])
def payment_callback(request):
        
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            try:
                rec_data = request.data.dict()     #loading body string to json data

            except:
                return JsonResponse(output_format(message='Wrong data format.'))
    
                        # authorize razorpay client with API Keys.
            client = razorpay.Client(auth=(base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_ID']), 
                                                    base64decode(RAZORPAY_CONFIGS['RAZOR_KEY_SECRET'])))
            if "razorpay_signature" in rec_data:

            # Verifying Payment Signature
                razorpay_response = client.utility.verify_payment_signature(rec_data)
            # if we get here Ture signature
                if razorpay_response:
                    data = {}

                    data['status'] = 'Success!'
                    data['payment_id'] = rec_data['razorpay_payment_id']
                    data['signature_id'] = rec_data['razorpay_signature']
                    
                    return JsonResponse(output_format(message='Success!', data=data))
                else:
                    return JsonResponse(output_format(message='Signature incorrect.'))
            else:
                return JsonResponse(output_format(message='Not received response.'))
                
@api_view(['POST'])
def contact_us(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse(output_format(message='Wrong data format.'))
        
        data['_id'] = create_unique_object_id()
        data['status'] = 'unseen'
        data['date'] = datetime.datetime.now()
        data['is_deleted'] = False
        
        try:
            result = database['Contact-us'].insert_one(document=data)
            print(result.inserted_id)
            return JsonResponse(output_format(message='Success!'))
        except:
            return JsonResponse(output_format(message='Message not send.'))


@api_view(['GET', 'PATCH', 'DELETE'])
def admin_contact_us(request, _id=None):
    
    if request.method == 'GET':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            # fetching all messages from contact us form
            data = database['Contact-us'].aggregate([
                                            {
                                                '$match': 
                                                {'is_deleted': False}
                                            },
                                            {
                                                '$lookup': {
                                                'from': "User",
                                                'localField': "email",
                                                'foreignField': "email",
                                                'as': "user"
                                                }
                                            },
                                            {
                                                '$project': {
                                                '_id': 1,
                                                'name': 1,
                                                'email': 1,
                                                'is_user': {
                                                        '$cond': {
                                                        'if': { '$size': "$user" },
                                                        'then': 'User',
                                                        'else': 'Guest'
                                                        }
                                                    }
                                                }
                                            }
                                        ])
            
            data = [i for i in data]
            
            if not data:
                return JsonResponse(output_format(message='No messages found.'))
            else:
                return JsonResponse(output_format(message='Success!', data=data))
        else:
            return JsonResponse(output_format(message='User not admin.'))
    
    elif request.method == 'PATCH':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            if _id == None:
                return JsonResponse(output_format(message='Message id not received.'))
            else:
                
                try:
                    data = json.loads(request.body)
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                result = database['Contact-us'].update_one({'_id': _id}, {'$set': data})
                
                if result.modified_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Update failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))
        
    elif request.method == 'DELETE':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            if _id == None:
                return JsonResponse(output_format(message='Message id not received.'))
            else:

                result = database['Contact-us'].update_one({'_id': _id}, {'$set': {'is_deleted': True}})
                
                if result.modified_count == 1:
                    return JsonResponse(output_format(message='Success!'))
                else:
                    return JsonResponse(output_format(message='Delete failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

@api_view(['GET'])
def admin_count_messages(request):
    
    if request.method == 'GET':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

            # fetching all messages from contact us form
            try:
                data = {}
                data['message_count'] = database['Contact-us'].count_documents({'status': 'unseen', 'is_deleted': False})
                return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Count failed.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))
 

@api_view(['GET'])
def rating_products(request, order_id=None):
    
    if request.method == 'GET':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            # fetching all messages from contact us form
            if order_id is None:
                return JsonResponse(output_format(message='Order id not received.'))
            else:
                data = database["Order"].aggregate([
                        { '$match': { '_id': order_id, 'user_id': user['_id']} },
                        {
                            '$lookup': {
                                'from': "Product",
                                'localField': "Order-details.prod_id",
                                'foreignField': "_id",
                                'as': "Product",
                            },
                        },
                        { '$unwind': "$Product" },
                        {
                            '$project': {
                                '_id': 0,
                                'prod_id': "$Product._id",
                                'prod_name': "$Product.prod_name",
                                'prod_image': { '$arrayElemAt': ["$Product.prod_image", 0] },
                            },
                        },
                    ])
                data = list(data)
                if not data:
                    return JsonResponse(output_format(message='Order not found.'))
                else:
                    return JsonResponse(output_format(message='Success!', data=data))
        else:
            return JsonResponse(output_format(message='User not customer.'))


@api_view(['GET', 'POST'])
def customer_rating(request, order_id=None):
    
    if request.method == 'POST':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:

            if order_id == None:
                return JsonResponse(output_format(message='Order id not received.'))
            else:
                
                #loading rating data from request
                try:
                    data = json.loads(request.body)
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))
                
                for product_rating in data:
                    
                    if database['Product'].find_one({'_id': product_rating.get('prod_id')}) is None:
                        return JsonResponse(output_format(message='Rated product not found.'))
                    else:
                        product_rating['order_id'] = order_id
                        product_rating['user_id'] = user['_id']
                        product_rating['date'] = datetime.datetime.now()
                        product_rating['_id'] = create_unique_object_id()
                        product_rating['rating'] = float(product_rating['rating'])

                        database['Rating'].insert_one(product_rating)
                
                return JsonResponse(output_format(message='Success!'))             
        else:
            return JsonResponse(output_format(message='User not customer.'))
    
    
    elif request.method == 'GET':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'customer' and user['_id'] == request.id:
            
            # fetching all messages from contact us form
            if order_id is None:
                return JsonResponse(output_format(message='Order id not received.'))
            else:
                data = database['Rating'].find({'order_id': order_id, 'user_id': user['_idfadmin_']}, 
                                               {'_id': 0,
                                                'user_id': 0,
                                                })
                
                data = list(data)
                
                if not data:
                    return JsonResponse(output_format(message='Rating not found.'))
                else:
                    return JsonResponse(output_format(message='Success!', data=data))    
        else:
            return JsonResponse(output_format(message='User not customer.'))
    
@api_view(['POST'])
def sales_report(request):
    
    print(request.method)
    if request.method == 'POST':
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is customer
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            try:
                resp_data = json.loads(request.body)     #loading body string to json data          
                resp_data['from_date'] = datetime.datetime.strptime(resp_data['from_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                resp_data['until_date'] = datetime.datetime.strptime(resp_data['until_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
                
            
            data = database["Order"].aggregate([
                        {
                            '$match': {
                            'order_status': { '$in': ["Pending"] },
                            'order_date': { '$gte': resp_data['from_date'], '$lt': resp_data['until_date'] },
                            },
                        },
                        { '$unwind': "$Order-details" },
                        {
                            '$project': {
                            '_id': 0,
                            'prod_id': "$Order-details.prod_id",
                            'prod_qty': { '$objectToArray': "$Order-details.prod_qty" },
                            },
                        },
                        { '$unwind': "$prod_qty" },
                        {
                            '$project': {
                            'prod_id': "$prod_id",
                            'size': "$prod_qty.k",
                            'qty': "$prod_qty.v",
                            },
                        },
                        {
                            '$group': {
                            '_id': { 'product_id': "$prod_id", 'prod_size': "$size" },
                            'Quantity': { '$sum': "$qty" },
                            },
                        },
                        {
                            '$project': {
                            '_id': 0,
                            'prod_id': "$_id.product_id",
                            'prod_size': "$_id.prod_size",
                            'total_qty': "$Quantity",
                            },
                        },
                        {
                            '$lookup': {
                            'from': "Product",
                            'localField': "prod_id",
                            'foreignField': "_id",
                            'as': "Product",
                            },
                        },
                        {
                            '$unwind': "$Product",
                        },
                        {
                            '$project': {
                            "Product name": "$Product.prod_name",
                            "Product size": "$prod_size",
                            "Total quantity": "$total_qty",
                            "Product price": "$Product.prod_price",
                            },
                        },
                        { '$sort': { "Product name": 1 } },
                        ])
            
            data = list(data)
            # print(list(data))
            if not data:
                return JsonResponse(output_format(message='Records not found.'))
            else:
                # print(list(data)[0])
                df = pd.DataFrame(data)
                df['Sub total'] = df['Product price'] * df['Total quantity']
                total = pd.DataFrame([{
                            "Product name": "Total",
                            # "Product size": ,
                            # "Total quantity": ,
                            "Sub total": sum(df['Sub total'])
                        }])
                new = pd.concat([df,total], ignore_index=True)
                new.index+=1

                file = open(f'{MEDIA_ROOT}/sdf.xlsx', 'wb+')
                new.to_excel(file, index_label="No.")
                file.seek(0)
                # print(file.read())
                response = FileResponse(file)
                file_name = f"sales_report_{str(resp_data['from_date'].date())}_{str(resp_data['until_date'].date())}.xlsx"
                response['Content-Type'] = 'application/vnd.ms-excel'
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                date = datetime.datetime.now()
                date.date()
                pass
                return response
                # return JsonResponse(output_format(message='Success!', data=data))
        else:
            return JsonResponse(output_format(message='User not customer.'))

 
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





# Checkout
#     > Cart
#         > grab all the items from cart and put into checkout page and clear the cart
#         > 
#     > Buy Now!
#         > direct checkout page
