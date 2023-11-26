from django.shortcuts import render,redirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import Cart,Order,Orderitem,Product,Profile,Coupon
from django.contrib.auth.models import User
import random
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string

from django.utils import timezone

# ...START- FUNCTION OF CHECKOUT PAGE...
@login_required(login_url='loginpage')
def index(request):
    '''CHECKOUT PAGE FUNCTION '''
    cartitems = Cart.objects.select_related('product').filter(user=request.user)
    for item in cartitems:
        if item.product_qty > item.product.quantity:
            Cart.objects.delete(id=item.id)
            
    # cartitems = Cart.objects.select_related('product').filter(user=request.user)
    total_price = 0
    for item in cartitems:
        total_price = total_price + item.product.selling_price * item.product_qty
        
    userprofile = None
    try:
        userprofile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        pass
    if request.method == 'POST':
        code = request.POST.get('code')  # Getting the entered coupon code
        if code == 'remove_coupon':
            # Remove the coupon from the session
            if 'discount_total' in request.session:
                del request.session['discount_total']
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
            messages.success(request,"Coupon Removed Successfully")
            return redirect('checkout')
        else:
            # Process the coupon code as needed
            current_time = timezone.now()
            try:
                coupon_obj = Coupon.objects.get(code=code)
                if coupon_obj.valid_to >= current_time and coupon_obj.active:
                    if coupon_obj.usage_count < coupon_obj.max_usage:
                # Increment the usage count for the coupon
                        coupon_obj.usage_count += 1
                        coupon_obj.save()

                        get_discount = (coupon_obj.discount / 100) * total_price
                        total_price_after_discount = total_price - get_discount
                        request.session['discount_total'] = total_price_after_discount
                        request.session['coupon_code'] = code
                        messages.success(request, "Coupon applied successfully")
                        return redirect('checkout')
                    else:
                        messages.error(request, "Coupon usage limit reached")
                        return redirect('checkout')
                else:
                    messages.error(request, "Coupon code is expired")
                    return redirect('checkout')
            except Coupon.DoesNotExist:
                # Handle the case where the coupon code does not exist
                messages.error(request, "Invalid coupon code")
    total_price_after_discount = request.session.get('discount_total')
    coupon_code = request.session.get('coupon_code')
    context = {
            'cartitems':cartitems,
            'total_price':total_price, 
            'userprofile':userprofile,
            'coupon_code':coupon_code,
            'total_price_after_discount':total_price_after_discount,
            
            }
    return render(request,'store/checkout.html',context)
# ...END- FUNCTION OF CHECKOUT PAGE...




# ...START- FUNCTION OF PLACEORDER...
@login_required(login_url='loginpage')
def placeorder(request):
    '''PLACEORDER FUNCTION'''
    total_price_after_discount = None  # Initialize with a default value

    if request.method == "POST":
        currentuser = request.user
        if not currentuser.first_name:
            currentuser.first_name = request.POST.get('fname')
            currentuser.last_name = request.POST.get('lname')
            currentuser.save()

        # Check if the user's profile exists and create it if needed
        if not Profile.objects.filter(user=request.user).exists():
            userprofile = Profile()
            userprofile.user = request.user
            userprofile.phone = request.POST.get('phone')
            userprofile.address = request.POST.get('address')
            userprofile.city = request.POST.get('city')
            userprofile.state = request.POST.get('state')
            userprofile.country = request.POST.get('country')
            userprofile.pincode = request.POST.get('pincode')
            userprofile.save()

        cart = Cart.objects.select_related('product').filter(user=request.user)
        cart_total_price = 0

        for item in cart:
            cart_total_price += item.product.selling_price * item.product_qty
        
        # Retrieve the coupon code from the session
        code = request.session.get('coupon_code', None)

        if code:
            current_time = timezone.now()
            coupon_obj = Coupon.objects.filter(code=code, valid_to__gte=current_time, active=True).first()

            if coupon_obj:
                get_discount = (coupon_obj.discount / 100) * cart_total_price
                total_price_after_discount = cart_total_price - get_discount
                request.session['discount_total'] = total_price_after_discount
                messages.success(request, "Coupon applied successfully")
            else:
                # Coupon code is invalid, so remove it from the session
                del request.session['coupon_code']
                messages.error(request, "Coupon code is expired or invalid")
        else:
            total_price_after_discount = cart_total_price

        neworder = Order()
        neworder.user = request.user
        neworder.fname = request.POST.get('fname')
        neworder.lname = request.POST.get('lname')
        neworder.email = request.POST.get('email')
        neworder.phone = request.POST.get('phone')
        neworder.address = request.POST.get('address')
        neworder.city = request.POST.get('city')
        neworder.state = request.POST.get('state')
        neworder.country = request.POST.get('country')
        neworder.pincode = request.POST.get('pincode')

        neworder.payment_mode = request.POST.get('payment_mode')
        neworder.payment_id = request.POST.get('payment_id')

        neworder.total_price = cart_total_price
        neworder.total_price_after_discount = total_price_after_discount

        trackno = 'bookspot' + str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_no=trackno).exists():
            trackno = 'bookspot' + str(random.randint(1111111, 9999999))

        neworder.tracking_no = trackno
        neworder.save()

        neworderitems = Cart.objects.filter(user=request.user)
        for item in neworderitems:
            Orderitem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )

            # To decrease the product quantity from available stock
            orderproduct = Product.objects.filter(id=item.product_id).first()
            orderproduct.quantity = orderproduct.quantity - item.product_qty
            orderproduct.save()

        # To clear the user's cart
        Cart.objects.filter(user=request.user).delete()

        # Clear coupon-related session data
        if 'discount_total' in request.session:
            del request.session['discount_total']
        if 'coupon_code' in request.session:
            del request.session['coupon_code']

        # Send order received email to customer
        # ... (your email sending code)

        payMode = request.POST.get('payment_mode')
        if (payMode == "Paid by Razorpay"):
            return JsonResponse({'status': "Your order has been placed successfully"})
        else:
            messages.success(request, "Your order has been placed successfully")

    return redirect('/')
# ...END- FUNCTION OF PLACEORDER...




# ...START- FUNCTION OF RAZORPAY...
@login_required(login_url='loginpage')
def razorpaycheck(request):
    '''RAZORPAY FUNCTION'''
    # Calculate the total price after applying any discount
    total_price = Cart.objects.filter(user=request.user).aggregate(
        total_price=Sum(
            ExpressionWrapper(
                F('product__selling_price') * F('product_qty'),
                output_field=DecimalField()
            )
        )
    )['total_price'] or 0

    # Check if a discount was applied and get the discount amount
    discount_total = request.session.get('discount_total')

    # Pass both total price and discount_total to the Razorpay page
    return JsonResponse({'total_price': total_price, 'discount_total': discount_total})
# ...END- FUNCTION OF RAZORPAY...