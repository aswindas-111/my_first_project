from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from store.models import Product,Cart
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# ...START- FUNCTION OF ADD TO CART...
@login_required(login_url='loginpage')
def addtocart(request):
    '''FUNCTION OF ADD TO CART'''
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            product_check = Product.objects.get(id=prod_id)
            if(product_check):
                if(Cart.objects.filter(user=request.user.id,product_id = prod_id)):
                    return JsonResponse({'status' : 'Product Already in Cart'})
                else:
                    prod_qty = int(request.POST.get('product_qty'))

                    if product_check.quantity >= prod_qty :
                        Cart.objects.create(user=request.user,product_id=prod_id,product_qty=prod_qty)
                        return JsonResponse({'status' : 'Product Added Successfully'})

                    else:
                        return JsonResponse({'status' : 'Only ' + str(product_check.quantity) +  'Quantity Available'})              
            else:
                return JsonResponse({'status' : 'No Such Product Found'})          
        else:
            return JsonResponse({'status':'Login to continue'}) 
    return redirect('/')    
# ...END- FUNCTION OF ADD TO CART...




# ...START- FUNCTION OF VIEW CART PAGE...
@receiver([post_save, post_delete], sender=Cart)
def invalidate_cart_cache(sender, instance, **kwargs):
    # Construct the cache key based on the user's ID
    cache_key = f'cart_{instance.user.id}'

    # Delete the cached result associated with the cache_key
    cache.delete(cache_key)

@login_required(login_url='loginpage')
def viewcart(request):
    '''FUNCTION OF VIEW CART PAGE'''
    # Construct the cache key based on the user's ID
    cache_key = f'cart_{request.user.id}'
    
    # Check if the result is already in the cache
    cached_cart = cache.get(cache_key)

    if cached_cart is not None:
        context = {'cart': cached_cart}
    else:
        cart = Cart.objects.select_related('product').filter(user=request.user)
        context = {'cart': cart}

        # Cache the result for future requests
        cache.set(cache_key, cart, timeout=3600)  # Cache the result for 1 hour (you can adjust this value)

    return render(request, 'store/cart.html', context)
# ...END- FUNCTION OF VIEW CART PAGE...



      
# ...START- FUNCTION OF PRODUCT QUANTITY INCREMENT...
def updatecart(request):
    '''PRODUCT QUANTITY INCREMENT FUNCTION'''
    if request.method == 'POST':
        prod_id = int(request.POST.get("product_id"))
        if(Cart.objects.filter(user = request.user,product_id=prod_id)):
            prod_qty = request.POST.get('product_qty')
            cart = Cart.objects.get(product_id=prod_id,user=request.user)
            cart.product_qty = prod_qty
            cart.save()
        return JsonResponse({'status' : 'Updated Successfully'})
    return redirect('/')
# ...END- FUNCTION OF PRODUCT QUANTITY INCREMENT...




# ...START- FUNCTION OF DELETE CART...
def deletecartitem(request):
    '''DELETe CART FUNCTION'''
    if request.method == 'POST':
        prod_id = int(request.POST.get("product_id"))
        if(Cart.objects.filter(user = request.user,product_id=prod_id)):
            cartitem = Cart.objects.get(product_id=prod_id,user=request.user)
            cartitem.delete()
            
            # Check if a coupon code is applied and remove it
            if 'coupon_code' in request.session:
                del request.session['coupon_code']

        return JsonResponse({'status' : 'Updated Successfully'})
    return redirect('/')
# ...END- FUNCTION OF DELETE CART...          
        


    