
from django.urls import path, include, reverse
from . import views
from . import auth_views
# defining URI enpoints for all the APIs
urlpatterns = [

    # User endpoints
    path('user-profile/', views.user_profile, name="user-profile"),
    path('change-password/', views.change_password, name="change-password"),
    path('signup/', auth_views.signup, name="signup"),
    path('login/', auth_views.login, name="login"),
    # path('users/', views.myview, name="users"),


    path('navbar-shop-category/', view=views.navbar_shop_category, name='navbar-shop=category')
    
]