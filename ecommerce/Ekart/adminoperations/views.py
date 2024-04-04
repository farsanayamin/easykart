from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from accounts.models import Account
from store.models import Product,Variation
from category.models import Category
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404

from django.http import HttpResponseServerError
from datetime import date, timedelta
from django.db.models import Sum, Count
from datetime import datetime
from django.db.models import Q
from datetime import datetime
from category import models

from django.db.models import Q

@never_cache
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        print("email:",email)
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None and user.is_active and user.is_admin:
            login(request, user)
            print("this is farsana")
            messages.success(request, "Welcome, admin!")
            return redirect("adminhome")  # Redirect to admin dashboard
        else:
            messages.error(request, "Invalid email or password for admin.")
            return redirect("adminlogin")  # Redirect back to login page if authentication fails
    return render(request, "admin/admin_login.html")

    

@never_cache
def admin_home(request):

    if "email" not in request.session:
        if "username" in request.session:
            today = date.today()
            year = date.today().year
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            current_date = datetime.now().date()
    return render(request, 'admin/admin_home.html')

# admin  logout
@never_cache
def admin_logout(request):
    if "username" in request.session:
        request.session.flush()
    return redirect("adminlogin")

from django.shortcuts import render
from django.contrib.auth.models import User

def user_manage(request):
    if request.user.is_authenticated:
        # Assuming Account model is your custom user model, replace it with your actual user model
        #user = request.user
        user = Account.objects.filter(is_admin=False)
        context = {"user": user}
        return render(request, "admin/user_management.html", context)
    else:
        return render(request, "404.html", status=404)
    

# block user


def block_user(request, id):
    if request.user.is_authenticated:
        obj = Account.objects.get(id=id)
        obj.is_blocked = True
        obj.save()
        return redirect("usermanage")


# un block user


def un_block_user(request, id):
    if request.user.is_authenticated:
        obj = Account.objects.get(id=id)
        obj.is_blocked = False
        obj.save()
        return redirect("usermanage")
    
# search for user


def search_for_user(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            query = request.POST["query"]
            user = Account.objects.filter(username__icontains=query, is_admin=False)
            context = {
                "user": user,
            }
        return render(request, "admin/user_management.html", context)

#product manage
def product_manage(request):
    if request.user.is_authenticated:
        obj = Product.objects.select_related("category").all().order_by("-id")
        variants = Variation.objects.all()
        context = {"items": obj, "variants": variants}
        return render(request, "admin/product.html", context)
    else:
        return redirect("adminlogin")
    



  # Import your Category model

from django.utils.text import slugify

def add_product(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Process POST request data
            name = request.POST.get("name")
            category_id = request.POST.get("category")
            price = request.POST.get("price")
            description = request.POST.get("description")
            image = request.FILES.get("image")
            stock = request.POST.get("stock")
            is_available = request.POST.get('is_available', False)
            print(name, category_id, price, description, image)
            if name and category_id and price and description and image:
                try:
                    selected_category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    messages.error(request, "Invalid category")
                    return render(request, "admin/add_product.html")

                if int(price) > 0:
                    if not Product.objects.filter(product_name=name).exists():
                        # Generate slug from product_name
                        slug = slugify(name)
                        # Ensure slug is unique
                        unique_slug = slug
                        num = 1
                        while Product.objects.filter(slug=unique_slug).exists():
                            unique_slug = f"{slug}-{num}"
                            num += 1

                        obj = Product(
                            product_name=name,
                            slug=unique_slug,
                            category=selected_category,
                            price=price,
                            description=description,
                            images=image,
                            stock=stock,
                            is_available = is_available
                        )
                        obj.save()
                        messages.success(request, "Product added successfully")
                        return redirect("productmanage")  # Redirect to product management page
                    else:
                        messages.error(request, "Product already exists")
                else:
                    messages.error(request, "Price should be greater than 0")
            else:
                messages.error(request, "Please fill out all fields")

        # Fetch categories from the database
        categories = Category.objects.all()
        return render(request, "admin/add_product.html", {'categories': categories})
    else:
        return redirect("adminlogin")  # Redirect to login page if user is not authenticated

#edit product
def edit_product(request, product_id):
    if request.user.is_authenticated:
        # Retrieve the product instance to be edited
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == "POST":
            # Process POST request data
            name = request.POST.get("name")
            category_id = request.POST.get("category")
            price = request.POST.get("price")
            description = request.POST.get("description")
            image = request.FILES.get("image")
            stock = request.POST.get("stock")
            is_available = request.POST.get('is_available', False)
            
            if name and category_id and price and description:
                try:
                    selected_category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    messages.error(request, "Invalid category")
                    return render(request, "admin/edit_product.html", {'product': product})
                
                if int(price) > 0:
                    product.product_name = name
                    product.category = selected_category
                    product.price = price
                    product.description = description
                    product.stock = stock
                    product.is_available = is_available
                    
                    # Update image only if a new image is provided
                    if image:
                        product.images = image

                    product.save()
                    messages.success(request, "Product updated successfully")
                    return redirect("productmanage")  # Redirect to product management page
                else:
                    messages.error(request, "Price should be greater than 0")
            else:
                messages.error(request, "Please fill out all fields")

        # Fetch categories from the database
        categories = Category.objects.all()
        return render(request, "admin/edit_product.html", {'product': product, 'categories': categories, id:product_id})
    else:
        return redirect("adminlogin")  # Redirect to login page if user is not authenticated




def list_product(request, id):
    obj = Product.objects.get(id=id)
    obj.is_available = True
    obj.save()
    return redirect("productmanage")

def un_list_product(request, id):
    obj = Product.objects.get(id=id)
    obj.is_available = False
    obj.save()
    return redirect("productmanage")

# delete product
def delete_product(request, id):
    Product.objects.get(id=id).delete()
    messages.success(request, "product deleted successfully")
    return redirect("adminproductmanage")

'''
# search for product
def search_product(request):
    if request.method == "POST":
        query = request.POST["query"]
        obj = Product.objects.filter(name__icontains=query)
        variants = variant.objects.filter(product_id__name__icontains = query)
        context = {"items": obj,"variants": variants}
        return render(request, "product.html", context)
'''


def search_product(request,id):
    pass
    


# add variant
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from store.models import Variation, Product


def add_variant(request, pro_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=pro_id)
        color = request.POST.get("color")
        size = request.POST.get("size")
        stock = int(request.POST.get("qnty"))
        
        if color:
            if not Variation.objects.filter(variation_category='color', variation_value=color, product=product).exists():
                if stock >= 0:
                    Variation.objects.create(product=product, variation_category='color', variation_value=color, is_active=True)
                    messages.success(request, "Color variant added successfully.")
                else:
                    messages.error(request, "The quantity is invalid.")
            else:
                messages.error(request, "The color variant is already added, please update it.")
        else:
            messages.error(request, "Color is required.")

        if size:
            if not Variation.objects.filter(variation_category='size', variation_value=size, product=product).exists():
                if stock >= 0:
                    Variation.objects.create(product=product, variation_category='size', variation_value=size, is_active=True)
                    messages.success(request, "Size variant added successfully.")
                else:
                    messages.error(request, "The quantity is invalid.")
            else:
                messages.error(request, "The size variant is already added, please update it.")
        else:
            messages.error(request, "Size is required.")
        
        return redirect("productmanage")
    
   



# variant quantity updatin
from django.shortcuts import render, redirect
from django.contrib import messages
from store.models import Variation

def edit_variant_stock(request, var_id):
    if request.method == "POST":
        quantity = int(request.POST["qnty"])
        if quantity > 0:
            obj = Variation.objects.get(id=var_id)
            obj.quantity = quantity
            obj.save()
            messages.success(request, "Variant quantity updated successfully.")
        else:
            messages.error(request, "The quantity is invalid.")
    return redirect("productmanage")

   