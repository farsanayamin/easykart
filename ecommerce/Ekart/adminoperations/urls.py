from django.urls import path
from .import views
from django.contrib import admin

urlpatterns = [
    path("adminlogin/", views.admin_login, name="adminlogin"),
    path("adminhome/", views.admin_home, name="adminhome"),
    path("usermanage/", views.user_manage, name="usermanage"),
    path("blockuser/<str:id>", views.block_user, name="blockuser"),
    path("unblockuser/<str:id>", views.un_block_user, name="unblockuser"),
    path("searchuser/", views.search_for_user, name="searchuser"),
    path("productmanage/",views.product_manage, name="productmanage"),
    path("addproduct/", views.add_product, name="addproduct"),
    path("editproduct/<int:product_id>", views.edit_product, name="editproduct"),
    path("searchforproduct/", views.search_product, name="searchforproduct"),
    path("listproduct/<str:id>/", views.list_product, name="listproduct"),
    path("unlistproduct/<str:id>/", views.un_list_product, name="unlistproduct"),
    path("addvariant/<int:pro_id>/", views.add_variant, name="addvariant"),
    path(
        "editvariantstock/<str:var_id>/",
        views.edit_variant_stock,
        name="editvariantstock",
    ),

    #category
    path("category/", views.show_category, name="category"),
    path("addcategory/", views.add_category, name="addcategory"),
    path("editcategory/<str:id>/", views.edit_category, name="editcategory"),
    path("search/", views.search, name="search"),
    path("listcategory/<str:id>", views.list_category, name="listcategory"),
    path("unlistcategory/<str:id>", views.un_list_category, name="unlistcategory"),
    path("adminlogout/", views.admin_login, name="adminlogout")
    
]
