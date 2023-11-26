from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from store.models import Wishlist,Product
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# ...START- FUNCTION OF WISHLIST INDEX PAGE...
@receiver([post_save, post_delete], sender=Wishlist)
def invalidate_cache(sender, instance, **kwargs):
    # Construct the cache key based on the user's ID
    cache_key = f"wishlist_{instance.user_id}"

    # Delete the cached result associated with the cache_key
    cache.delete(cache_key)

@login_required(login_url='loginpage')
def index(request):
    '''FUNCTION OF WISHLIST INDEX PAGE'''
    # Check if the result is already in the cache
    cache_key = f"wishlist_{request.user.id}"
    cached_wishlist = cache.get(cache_key)

    if cached_wishlist is not None:
        context = {'wishlist': cached_wishlist}
    else:
        wishlist = Wishlist.objects.filter(user=request.user).select_related('product')
        context = {'wishlist': wishlist}

        # Cache the result for future requests
        cache.set(cache_key, wishlist, timeout=3600)  # Cache the result for 1 hour (you can adjust this value)

    return render(request, 'store/wishlist.html', context)
# ...START- FUNCTION OF WISHLIST INDEX PAGE...




# ...START- ADD TO WISHLIST FUNCTION...
@receiver([post_save, post_delete], sender=Wishlist)
def invalidate_wishlist_cache(sender, instance, **kwargs):
    # Construct the cache key based on the user's ID
    cache_key = f'wishlist_{instance.user.id}'

    # Delete the cached result associated with the cache_key
    cache.delete(cache_key)

def addtowishlist(request):
    '''ADD TO WISHLIST'''
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            product_check = Product.objects.filter(id=prod_id).first()

            if product_check:
                # Perform the necessary database operations
                wishlist, created = Wishlist.objects.get_or_create(user=request.user, product_id=prod_id)

                # Invalidate the wishlist cache after the change
                invalidate_wishlist_cache(sender=Wishlist, instance=wishlist)

                return JsonResponse({'status': 'product added to wishlist'})
            else:
                return JsonResponse({'status': 'no such product found'})
        else:
            return JsonResponse({'status': 'Login to continue'})

    return redirect('/')
# ...END- ADD TO WISHLIST FUNCTION...




# ...START- DELETE WISHLIST FUNCTION...
@receiver(post_delete, sender=Wishlist)
def invalidate_wishlist_cache(sender, instance, **kwargs):
    # Construct the cache key based on the user's ID
    cache_key = f'wishlist_{instance.user.id}'

    # Delete the cached result associated with the cache_key
    cache.delete(cache_key)

def deletewishlistitem(request):
    '''DELETe WISHLIST FUNCTIONALITY'''
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            user = request.user
            
            # Construct the cache key based on the user's ID
            cache_key = f'wishlist_{user.id}'

            # Use filter to get a queryset of matching Wishlist items
            wishlist_items = Wishlist.objects.filter(user=user, product_id=prod_id)
            
            if wishlist_items.exists():
                # Delete all matching items in the queryset
                wishlist_items.delete()
                
                # Invalidate the user's wishlist cache
                cache.delete(cache_key)
                
                return JsonResponse({'status': 'Product removed from wishlist'})
            else:                
                return JsonResponse({'status': 'Product not found in wishlist'})
        else:
            return JsonResponse({'status': 'Login to continue'})

    return redirect('/')
# ...START- DELETE WISHLIST FUNCTION...