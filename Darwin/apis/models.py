from django.db import models
from mongoengine import Document, fields, connect, QuerySet
# Create your models here.

connect('mystore', host="mongodb://127.0.0.1", port=27017, alias='mystore1')

# class AwesomerQuerySet(QuerySet):

#     def get_awesome(self):
#         return self.all()

class User(Document):
    id = fields.StringField(max_length=7, primary_key = True)
    name = fields.StringField()
    email = fields.StringField(unique=True, required=True)
    password = fields.StringField(required=True)
    mobile_no = fields.LongField()

    meta = {'db_alias' : 'mystore1', 'collection' : 'User'}



