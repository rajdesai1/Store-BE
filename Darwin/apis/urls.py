
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

    #password reset
    path('request-password-reset/', views.request_password_reset, name='request-password-reset'),
    path('reset-password/', views.reset_password, name='reset-password'),


    path('navbar-shop-category/', views.navbar_shop_category, name='navbar-shop-category'),

    #Admin panel
    path('admin-supplier/', views.supplier, name='admin-supplier'),
    path('admin-supplier/<str:_id>/', views.supplier, name='admin-supplier'),   #done   #patch #update

    path('admin-category-type/', views.cat_type, name='admin-category-type'),
    path('admin-category-type/<str:_id>/', views.cat_type, name='admin-category-type'), #done   #patch  #delete

    path('admin-category/', views.admin_category, name='admin-category'),
    path('admin-category/<str:_id>/', views.admin_category, name='admin-category'),     #done   #patch  #delete

    path('admin-cat-type-to-category/<str:_id>/', views.admin_cat_type_to_category, name='admin-cat-type-to-category'),
    
    path('admin-product/', views.admin_product, name='admin-product'),
    path('admin-product/<str:_id>/', views.admin_product, name='admin-product'),    #done   #patch  #delete

    path('admin-purchase/', views.admin_purchase, name='admin-purchase'),
    path('admin-purchase/<str:_id>/', views.admin_purchase, name='admin-purchase'),     #done   #patch

    path('product-discount/', views.product_discount, name='product-discount'),
    path('product-discount/<str:_id>/', views.product_discount, name='product-discount'),   #done

    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),

    # path('invoice/', views.invoice, name='invoice'),



    #customer side
    path('customer-address/', views.customer_address, name='customer-address'),
    path('customer-address/<str:_id>/', views.customer_address, name='customer-address'),   #done

    path('check-discount-code/', views.check_discount_code, name='check-discount-code'),
    path('customer-order/', views.customer_order, name='customer-order'),


    #open apis
    path('customer-product/', views.customer_product, name='customer-product'),
    path('customer-product/<str:_id>/', views.customer_product, name='customer-product'),
]