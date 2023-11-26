from django.db import models
from django.contrib.auth.models import User
import datetime
import os
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

def get_file_path(request,filename):
    original_filename = filename
    nowTime = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (nowTime,original_filename)
    return os.path.join('uploads/',filename)

'''BANNER'''
class Banner(models.Model):
    image = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    status = models.BooleanField(default=True,help_text="0=hidden,1=show")
    created_at = models.DateTimeField(auto_now_add=True)

'''MODEL FOR AUTHORS SLIDER/CAROUSEL TO STORE THEIR IMAGE,DESCRIPTION'''
class Author(models.Model):
    name = models.CharField(max_length=150,null=False,blank=True)
    author_image = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    small_description = models.TextField(max_length=500,null=False,blank=False)
    description = models.TextField(max_length=5000,null=False,blank=False)    
    
    
    def __str__(self):
        return self.name
    
'''TESTIMONIALS-HOME PAGE'''
class Testimonial(models.Model):
    name = models.CharField(max_length=150,null=False,blank=True)
    testimonial = models.TextField(max_length=100,null=False,blank=False)
    status = models.BooleanField(default=True,help_text="0=hidden,1=show")

    def __str__(self):
        return self.name

'''CATEGORY SLIDER IN HOME PAGE'''
class Category_slider(models.Model):
    name = models.CharField(max_length=150,null=False,blank=False)
    image = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name

'''CATEGORY'''
class Category(models.Model):
    name = models.CharField(max_length=150,null=False,blank=False)
    image = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    description = models.TextField(max_length=500,null=False,blank=False)
    status = models.BooleanField(default=False,help_text="0=default,1=Hidden")
    trending = models.BooleanField(default=False,help_text="0=default,1=Trending")
    created_at = models.DateTimeField(auto_now_add=True)
    searchablefields = ['name']
    
    def __str__(self):
        return self.name
    
'''PRODUCT'''
class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=150,null=False,blank=False)
    product_image = models.ImageField(upload_to=get_file_path,null=True,blank=True)
    small_description = models.TextField(max_length=1000,null=False,blank=False)
    language = models.CharField(max_length=50,null=False,blank=False)
    author = models.CharField(max_length=50,null=False,blank=False)
    quantity = models.IntegerField(null=False,blank=False)
    original_price = models.FloatField(null=False,blank=False)
    selling_price = models.FloatField(null=False,blank=False)
    status = models.BooleanField(default=False,help_text="0=default,1=Hidden")
    trending = models.BooleanField(default=False,help_text="0=default,1=Trending")
    created_at = models.DateTimeField(auto_now_add=True)
    searchablefields = ['name','language']
    
    def __str__(self):
        return self.name
    
    
'''USERS WITHOUT COMPLETED ORDER,THAT IS, USERS CAN BE ONLY ADD TO CART,THEY CAN BE STORED IN THIS TABLE'''
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_qty = models.IntegerField(null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return self.user.username

'''WISHLIST'''
class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


'''ORDER'''
class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    fname = models.CharField(max_length=150,null=False)
    lname = models.CharField(max_length=150,null=False)
    email = models.CharField(max_length=150,null=False)
    phone = models.CharField(max_length=150,null=False)
    address = models.TextField(null=False)
    city = models.CharField(max_length=150,null=False)
    state = models.CharField(max_length=150,null=False)
    country = models.CharField(max_length=150,null=False)
    pincode = models.CharField(max_length=150,null=False)
    total_price = models.FloatField(null=False)
    total_price_after_discount = models.FloatField(null=True)
    payment_mode = models.CharField(max_length=150,null=False)
    payment_id = models.CharField(max_length=250,null=True)
    orderstatuses = (
        ('Pending','Pending'),
        ('Out for shipping','Out for shipping'),
        ('Completed','Completed'),
    )
    status = models.CharField(max_length=150,choices = orderstatuses, default='pending')
    tracking_no = models.CharField(max_length=150,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    searchablefields = ['fname','lname','email','state']
    
    
    def __str__(self):
        return self.user.username
    
    
'''ONE ORDER HAS MULTIPLE ITEMS ,THAT CAN BE STORED THIS MODEL'''
class Orderitem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)
    searchablefields = ['order__fname','order__lname','product__name','product__language','product__author']
    
    
    def __str__(self):
        return self.order.fname


'''PROFILE (DURING THE ORDER PLACEMENT)'''
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=150,null=False)
    address = models.TextField(null=False)
    city = models.CharField(max_length=150,null=False)
    state = models.CharField(max_length=150,null=False)
    country = models.CharField(max_length=150,null=False)
    pincode = models.CharField(max_length=150,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username


'''COUPON'''
class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    valid_from = models.DateTimeField()  # Corrected: Added parentheses
    valid_to = models.DateTimeField()    # Corrected: Added parentheses
    discount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(70)])
    active = models.BooleanField(default=False)
    usage_count = models.PositiveBigIntegerField(default=0)
    max_usage = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return self.code
    
    
