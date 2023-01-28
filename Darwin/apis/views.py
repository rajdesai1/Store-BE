from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .db import database, client
from .utils import pwd_context, output_format, create_unique_object_id
import pyrebase
from django.core.files.storage import default_storage
from Darwin.settings import FIREBASECONFIG
import os
import datetime

# Create your views here.

def myview(request):
    # url = reverse('view_post', args=[23425678])
    # print(url)
    
    return HttpResponse("<h1>Hah! Nothing here.</h1>")



@api_view(['GET'])
def user_profile(request):
    print(request.id)
    print(request.role)
    if request.id:
        user = database['User'].find_one({'_id' : request.id})
    
    print(user.pop('password'))
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


@api_view(['GET'])
def navbar_shop_category(request):
        cats = database['Category-type'].find()
        out = [i for i in cats]
        print(out)
        print('s')
        return JsonResponse(output_format(data=out))


@api_view(['GET', 'POST'])
def supplier(request):

##### for adding suppliers from admin panel(one supplier)
    if request.method == 'POST':
        
        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        # checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            data = request.data.dict()

            # converting fields into int
            try:
                data['mobile_no'] = int(data['mobile_no'])
                data['pincode'] = int(data['pincode'])
            except:
                return JsonResponse(output_format(message='Wrong data format.'))
            
            #inserting data
            try:
                data['_id'] = create_unique_object_id()
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

            #getting and returning all the suppliers from the db
            try:
                data = database['Supplier'].find()
                data = [i for i in data]
                print(data)
                return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Suppliers not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


@api_view(['POST', 'GET'])
def cat_type(request):

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
                    data['active'] =  True if data['active'] == 'true' or 'True' else False
                    data['cat_type'] = data['cat_type']
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))

                #inserting data
                try:
                    data['_id'] = create_unique_object_id()
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

            #getting and returning all the category-type from the db
            try:
                data = database['Category-type'].find()
                data = [i for i in data]
                print(data)
                return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Category-type not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))

@api_view(['POST', 'GET'])
def admin_category(request):

##### for adding category from admin panel
    if request.method == 'POST':

        #fetching admin details
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})
        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:
            
            data = request.data.dict()
            #checking if category already exists
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
                    data['active'] =  True if data['active'] == 'true' or 'True' else False
                    data['cat_title'] = data['cat_title']
                except:
                    return JsonResponse(output_format(message='Wrong data format.'))

                #inserting data
                try:
                    data['_id'] = create_unique_object_id()
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
                        '$project': {
                            '_id':'$Category._id',
                            'cat_type_id': '$_id',
                            'cat_type': '$cat_type',
                            'active': '$Category.active',
                            'cat_title': '$Category.cat_title',
                        }
                    }
                ]

                data = database['Category-type'].aggregate(pipeline=pipeline)
                data = [i for i in data]
                print(data)
                return JsonResponse(output_format(message='Success!', data=data))
            except:
                return JsonResponse(output_format(message='Category not fetched.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


@api_view(['POST', 'GET'])
def admin_product(request):

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
                data['active'] = True if request.POST['active'] == 'true' or 'True' else False
                data['prod_desc'] = request.POST['prod_desc']
                data['created_at'] = datetime.datetime.now()
                data['prod_price'] = request.POST['prod_price']
                data['prod_qty'] = {}
                data['prod_image'] = []

                #renaming all product images and uploading to firebase
                for i, file in enumerate(request.FILES.values()):
                    filename, fileextension = os.path.splitext(file.name)
                    if fileextension not in ['.png', '.jpg', 'jpeg', '.webp']:
                        return JsonResponse(output_format(message='Uploaded file is not an image.'))
                    
                    new_name = f"{prod_id}-{str(i)}{os.path.splitext(file.name)[1]}"
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
            
            #and finally inserting product to the db
            try:
                    data['_id'] = prod_id
                    database['Product'].insert_one(data)
                    return JsonResponse(output_format(message='Success!'))
            except:
                    return JsonResponse(output_format(message='Category not inserted.'))
        else:
            return JsonResponse(output_format(message='User not admin.'))


##### for getting products into admin panel
    if request.method == 'GET':
        #fetching user data
        user = database['User'].find_one(filter={'_id':request.id, 'role':request.role})

        #checking if user is admin
        if user['role'] == 'admin' and user['_id'] == request.id:

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
                        '$project': {
                            '_id': '$Product._id',
                            'prod_name': '$Product.prod_name',
                            'cat_type': '$cat_title',
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
        else:
            return JsonResponse(output_format(message='User not admin.'))




























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

