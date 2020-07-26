from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from admin_app.models import *

from citycourier import settings


class MyDeliveries(View):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        delivery_person = UserDetails.objects.get(user=self.request.user)
        deliveries = Delivery.objects.filter(delivery_person=delivery_person)
        return render(self.request, "my_deliveries.html", {"deliveries": deliveries, "user": delivery_person})

    @method_decorator(login_required)
    def post(self, *args, **kwargs):
        action = self.request.POST.get("action")
        delivery_id = self.request.POST.get("order_id")
        print(delivery_id)
        if action == "Pick Up":
            status = "Picked"
            subject = "Order Picked"
            content = "Your order is picked and is on the way."

        elif action == "Cancel":
            status = "Cancelled"
            delivery_person = UserDetails.objects.get(user=self.request.user)
            UserDetails.objects.filter(id=delivery_person.id).update(delivery_person_availability="AVAILABLE")
            subject = "Order Cancelled"
            content = "Your order was cancelled."

        elif action == "Complete Delivery":
            status = "Delivered"
            delivery_person = UserDetails.objects.get(user=self.request.user)
            UserDetails.objects.filter(id=delivery_person.id).update(delivery_person_availability="AVAILABLE")
            subject = "Order Delivered"
            content = "Your order was delivered successfully"

        Delivery.objects.filter(id=delivery_id).update(current_status=status)
        delivery = Delivery.objects.get(id=delivery_id)
        customer = UserDetails.objects.get(id=delivery.customer.id)
        my_email = settings.EMAIL_HOST_USER
        send_mail(subject,
                  content, my_email,
                  [customer.user.username])

        return redirect("mydeliveries")
