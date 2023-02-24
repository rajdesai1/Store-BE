
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
    path('admin-cat-to-product/<str:_id>/', views.admin_cat_to_product, name='admin-cat-to-product'),
    
    
    path('admin-product/', views.admin_product, name='admin-product'),
    path('admin-product/<str:_id>/', views.admin_product, name='admin-product'),    #done   #patch  #delete

    path('admin-purchase/', views.admin_purchase, name='admin-purchase'),
    path('admin-purchase/<str:_id>/', views.admin_purchase, name='admin-purchase'),     #done   #patch

    path('product-discount/', views.product_discount, name='product-discount'),
    path('product-discount/<str:_id>/', views.product_discount, name='product-discount'),   #done

    path('admin-contact-us/', views.admin_contact_us, name='admin-contact-us'),
    path('admin-contact-us/<str:_id>/', views.admin_contact_us, name='admin-contact-us'),
    path('admin-count-messages/', views.admin_count_messages, name='admin-count-messages'),
    
    path('admin-order/', views.admin_order, name='admin-order'),
    path('admin-order/<str:_id>/', views.admin_order, name='admin-order'),
    
    path('admin-user-count/', views.admin_user_count, name='admin-user-count'),
    
    path('admin-order-count/', views.admin_order_count, name='admin-order-count'),
    
    
    # reports
    path('sales-report/', views.sales_report, name='sales-report'),
    path('supplier-report/', views.supplier_report, name='supplier-report'),  
    path('stock-report/', views.stock_report, name='stock-report'),
    path('purchase-report/', views.purchase_report, name='purchase-report'),
    
    
    
    
    # path('add-to-cart/', views.add_to_cart, name='add-to-cart'),

    # path('invoice/', views.invoice, name='invoice'),



    #customer side
    path('customer-address/', views.customer_address, name='customer-address'),
    path('customer-address/<str:_id>/', views.customer_address, name='customer-address'),   #done

    path('check-discount-code/', views.check_discount_code, name='check-discount-code'),
    path('customer-order/', views.customer_order, name='customer-order'),
    
    path('verify-order/', views.verify_order, name='verify-order'),
    
    path('cart/', views.cart, name='cart'),     #done
    
    path('get-payment/', views.get_payment, name='get-payment'),

    path('cart-count/', views.cart_count, name='cart-count'),
    
    path('checkout-user-info/', views.checkout_user_info, name='checkout-user-info'),
    
    path('order-invoice/<str:_id>/', views.order_invoice, name='order-invoice'),
    
    path('rating-products/<str:order_id>/', views.rating_products, name='rating-products'),
    
    path('customer-rating/<str:order_id>/', views.customer_rating, name='customer-rating'),
    
    
    #open apis
    path('customer-product/', views.customer_product, name='customer-product'),
    path('customer-product/<str:_id>/', views.customer_product, name='customer-product'),
    path('contact-us/', views.contact_us, name='contact-us'),
    path('suggested-product/<str:cat_id>/', views.suggested_product, name='suggested-product'),
]