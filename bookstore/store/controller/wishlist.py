from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from store.models import Wishlist,Product
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# ...START- FUNCTION OF WISHLIST INDEX PAGE...
@login_required(login_url='loginpage')
def index(request):
    wishlist = Wishlist.objects.filter(user=request.user).select_related('product')
    context = {'wishlist':wishlist}
    return render(request,'store/wishlist.html',context)
# ...START- FUNCTION OF WISHLIST INDEX PAGE...




# ...START- ADD TO WISHLIST FUNCTION...
def addtowishlist(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            product_check = Product.objects.get(id=prod_id) 
            if(product_check):
                if(Wishlist.objects.filter(user=request.user,product_id=prod_id)):
                    return JsonResponse({'status':'product allready in wishlist'})
                else:
                    Wishlist.objects.create(user=request.user,product_id=prod_id)
                    return JsonResponse({'status':'product added to wishlist'})
            else:
                return JsonResponse({'status':'no such product found'})
        else:
            return JsonResponse({'status':'Login to continue'})

    return redirect('/')
# ...END- ADD TO WISHLIST FUNCTION...




# ...START- DELETE WISHLIST FUNCTION...
def deletewishlistitem(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))

            if(Wishlist.objects.filter(user=request.user, product_id=prod_id)):
                wishlistitem = Wishlist.objects.get(product_id=prod_id)
                wishlistitem.delete()
                return JsonResponse({'status':'product removed from wishlist'})
            else:                
                return JsonResponse({'status':'product not found in wishlist'})
        else:
            return JsonResponse({'status':'Login to continue'})

    return redirect('/')
# ...START- DELETE WISHLIST FUNCTION...