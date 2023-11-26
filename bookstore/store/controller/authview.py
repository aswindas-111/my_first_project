from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from store.forms import CustomUserForm
from django.http import HttpResponse,JsonResponse
from django.core.mail import send_mail
from bookstore.settings import EMAIL_HOST_USER
import random
from django.views.decorators.csrf import csrf_exempt
from store.models import User


# ...START- FUNCTION OF VERIFICATION OF EMAIL THROUGH OTP...
@csrf_exempt
def VerifyOTP(request):
    '''VERIFICATION OF OTP'''
    user = None
    if request.method == "POST":
        userotp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if userotp == str(stored_otp):
            registration_data = request.session.get('registration_data')
            
            # Create and save the user account in the database
            user = User.objects.create_user(
                username=registration_data['username'],
                email=registration_data['email'],
                password=registration_data['password1']
            )
            
            
            request.session.pop('registration_data')
            request.session.pop('otp')

            messages.success(request, "Registration successful. Please log in.")
            
            # Redirect to the login page after successful registration
            return redirect('loginpage')  # Use the URL name 'loginpage' here
        else:
            error_message = "Invalid OTP. Please try again."
            messages.error(request, error_message)
            
    if user is not None:
        pass
    return JsonResponse({'error': 'Invalid otp'}, status=400)
# ...END- FUNCTION OF VERIFICATION OF EMAIL THROUGH OTP...




# ...START- FUNCTION OF USER REGISTRATION...
def register(request):
    '''USER REGISTRATION'''
    if request.user.is_authenticated:
        messages.warning(request, "You are Logged in")
        return redirect('home')
    else:
        if request.method == 'POST':
            form = CustomUserForm(request.POST)
            if form.is_valid():
                request.session['registration_data'] = form.cleaned_data  # Store registration data in session
                otp = random.randint(100000, 999999)
                send_mail("User Data: ", f"Verify your mail by otp: {otp}", EMAIL_HOST_USER, [form.cleaned_data['email']], fail_silently=True)
                request.session['otp'] = otp  # Store OTP in session
                messages.success(request, "OTP sent successfully, please verify.")
                return render(request, 'store/auth/verify.html')
        else:
            form = CustomUserForm()
        context = {'form': form}
        return render(request, 'store/auth/register.html', context)
# ...END- FUNCTION OF USER REGISTRATION...




# ...START- FUNCTION OF LOGIN PAGE FUNCTIONALITY...
def loginpage(request):
    '''LOGIN PAGE FUNCTIONALITY'''
    if request.user.is_authenticated:
        messages.warning(request,"You are Logged in")
        return redirect('home')
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            passwd = request.POST.get('password')
            
            user = authenticate(request,username=name,password=passwd)
            
            if user is not None:
                login(request,user)
                messages.success(request,'Logged in successfully')
                return redirect('home')
            else:
                messages.error(request,"Invalid username or Password")
                return redirect('loginpage')
        
        return render(request,'store/auth/login.html')
# ...START- FUNCTION OF LOGIN PAGE FUNCTIONALITY...




    
# ...START- FUNCTION OF LOGOUT...
def logoutpage(request):
    '''LOGOUT'''
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logout Successfully")
    return redirect('home')
# ...END- FUNCTION OF LOGOUT...

