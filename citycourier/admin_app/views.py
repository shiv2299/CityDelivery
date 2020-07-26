import string
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from admin_app.models import *

# Create your views here.
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View

from citycourier import settings


def home(request):
    if request.user.is_authenticated:
        user = UserDetails.objects.get(user=request.user)
    else:
        user = "visitor"
    return render(request, "home.html",{"current_user":user})


def logout_user(request):
    logout(request)
    return redirect("login")


class LoginForm(View):

    def get(self, *args, **kwargs):
        return render(self.request, "login.html")

    def post(self, *args, **kwargs):
        details = self.request.POST.get
        user = authenticate(username=details("email"), password=details("password"))
        if user is not None:
            user_details = UserDetails.objects.get(user=user)
            if user_details.role == details("user_type"): #and user_details.is_verified:
                login(self.request, user)
                return JsonResponse(
                    {"status": True, "user_type": details("user_type"), "message": "Logged In successfully"})
            else:
                message = ""
                if user_details.role == "CA":
                    message = "Please use customer login"
                elif user_details.role == "SA":
                    message = "Please use admin login"
                elif user_details.role == "DP":
                    message = "Please use delivery person login"
                return JsonResponse({"status": False, "message": message})

        else:
            return JsonResponse({"status": False, "message": "Invalid credentials or no registered user found"})


class SignupForm(View):

    def get(self, *args, **kwargs):
        return render(self.request, "signup.html")

    def post(self, *args, **kwargs):
        try:
            data = self.request.POST.get
            exists = User.objects.filter(username=data("email")).exists()
            if exists:
                return JsonResponse({"success": "0", "message": "Email already registered"})
            user = User.objects.create_user(username=data("email"), email=data("email"), first_name=data("name"),
                                            password=data("password"))
            signedUp = UserDetails.objects.create(user=user, role="CA", contact=data("contact"), address=data("address"),
                                                  pin_code=data("pincode"))
            current_site = get_current_site(self.request)
            domain = current_site.domain
            token_string = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=20)
            )
            UserDetails.objects.filter(user=user).update(token=token_string)
            url = f"http://{domain}/verify/" + token_string
            subject = "Verify Your Account"
            email_from = settings.EMAIL_HOST_USER
            registered_user = User.objects.get(username=data("email"))
            recipient_list = [registered_user.username]
            html_message = render_to_string(
                "verify-account-template.html", {"first_name": registered_user.first_name, "url": url}
            )
            plain_message = strip_tags(html_message)
            status = send_mail(
                subject,
                plain_message,
                email_from,
                recipient_list,
                html_message=html_message,
            )
            return JsonResponse({"success": "1", "data": {"id": signedUp.id}, "message": "Account Created\nPleae verify your account using verification link sent to your email"}, safe=False)
        except:
            return JsonResponse({"success":"0","message":"Error Creating Account"})

def verify_account(request,token):
    token_user = UserDetails.objects.filter(token=token).update(is_verified=True)
    return redirect("login")

def add_admin(request):
    if request.method=="GET":
        return render(request,"add-admin.html")
    if request.method == "POST":
        data = request.POST.get
        try:
            user = User.objects.create_user(username=data("email"), email=data("email"), first_name=data("name"),password=data("password"))
            UserDetails.objects.create(user=user, role="SA", contact=data("contact"))
            return JsonResponse({"success": "1","message": "Admin Created"}, safe=False)
        except:
            return JsonResponse({"success": "0", "message": "Error Creating Account"})


def add_delivery_person(request):
    if request.method=="GET":
        return render(request,"add-delivery-person.html")
    if request.method == "POST":
        data = request.POST.get
        doc = request.FILES.get
        print(data)
        # try:
        user = User.objects.create_user(username=data("email"), email=data("email"), first_name=data("name"),password=data("password"))
        UserDetails.objects.create(user=user, role="DP", contact=data("contact"),verification_doc=doc("image"))
        return JsonResponse({"success": "1","message": "Delivery Person Added"}, safe=False)
        # except:
        #     return JsonResponse({"success": "0", "message": "Error Creating Account"})

def reset_password(request):
    if request.method=="GET":
        return render(request,"forgot_password.html")

    if request.method=="POST":
        email = request.POST.get("email")
        print("EMAIL",email)
        user = User.objects.filter(username=email).exists()
        if not user:
            return HttpResponse("User ndoes not exist")
        registered_user = User.objects.get(username=email)
        current_site = get_current_site(request)
        domain = current_site.domain
        token_string = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=20)
        )
        ResetPassword.objects.create(token=token_string,user=registered_user)
        url = f"http://{domain}/resetpassword/" + token_string
        subject = "Your password reset link"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [registered_user.username]
        html_message = render_to_string(
            "forgot_password_template.html", {"first_name": registered_user.first_name, "url": url}
        )
        plain_message = strip_tags(html_message)
        status = send_mail(
            subject,
            plain_message,
            email_from,
            recipient_list,
            html_message=html_message,
        )
        return HttpResponse("link sent")

class ResetPasswordView(View):
    def get(self,*args,**kwargs):
        return render(self.request, "resetpassword.html")

    def post(self,*args,**kwargs):
        data=self.request.POST.get
        token_user = ResetPassword.objects.get(token=kwargs["token"])
        status = token_user.user
        status.password = make_password(data("password"))
        status.save()
        return HttpResponse("Password changed")



class OrderAction(View):

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        deliveries = Delivery.objects.all()
        delivery_persons = UserDetails.objects.filter(role="DP", delivery_person_availability="AVAILABLE")
        return render(self.request, "delivery_action.html",
                      {"deliveries": deliveries, "delivery_persons": delivery_persons})

    @method_decorator(login_required)
    def post(self, *args, **kwargs):
        details = self.request.POST.get
        print(details("order_id"))
        if details("action") == "Accept":
            delivery_person = UserDetails.objects.get(id=details("delivery_person"))
            Delivery.objects.filter(id=details("order_id")).update(delivery_person=delivery_person,
                                                                   current_status="Accepted")
            delivery_count = Delivery.objects.filter(delivery_person=delivery_person).exclude(
                current_status="Delivered").exclude(current_status="Cancelled").count()
            if (delivery_count == 3):
                UserDetails.objects.filter(id=delivery_person.id).update(delivery_person_availability="BUSY")
            subject = "Order Accepted"
            message = "Your order is accepted. A delivery person will reach you soon to pick up the order"
        else:
            Delivery.objects.filter(id=details("order_id")).update(current_status="Cancelled")
            subject = "Order Cancelled"
            message = "Your order is cancelled please contact for further details"

        delivery = Delivery.objects.get(id=details("order_id"))
        my_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, my_email, [delivery.customer.user.username])

        return redirect("orderaction")



