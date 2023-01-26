
from django.urls import path, include, reverse
from . import views

# defining URI enpoints for all the APIs
urlpatterns = [

    # User endpoints
    path('users/', views.user_view, name="users"),
    # path('users/', views.myview, name="users"),


    
]

# print(reverse('view_post', args=[2]))