
from django.urls import path, include, reverse
from . import views
from . import auth_views
# defining URI enpoints for all the APIs
urlpatterns = [

    path('', views.myview, name="home page"),


    # User endpoints
    path('user-profile/', views.user_profile, name="user-profile"),
    path('change-password/', views.change_password, name="change-password"),
    path('signup/', auth_views.signup, name="signup"),
    path('login/', auth_views.login, name="login"),


    path('navbar-shop-category/', views.navbar_shop_category, name='navbar-shop-category'),

    #Admin panel
    path('admin-supplier/', views.supplier, name='admin-supplier'),
    path('admin-category-type/', views.cat_type, name='admin-category-type'),
    path('admin-category/', views.admin_category, name='admin-category'),
    path('admin-product/', views.admin_product, name='admin-product'),
]