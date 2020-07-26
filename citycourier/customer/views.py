import tempfile
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View
from weasyprint import HTML

from citycourier import settings
from django.shortcuts import render, redirect

# Create your views here.
from .forms import DeliveryForm
from admin_app.models import *


def add_delivery(request):
    form = DeliveryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        order = form.save()
        print(order)
        return redirect("confirmdelivery", pk=order.id)
    return render(request, "adddelivery.html", {"form": form})


class AddDelivery(View):

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        print(self.request.user)
        return render(self.request, "adddelivery.html")

    @method_decorator(login_required)
    def post(self, *args, **kwargs):
        data = self.request.POST.get
        image = self.request.FILES["photo"]
        user = self.request.user
        print("USER", user)
        cust = UserDetails.objects.get(user=user)
        order = Delivery.objects.create(customer=cust, delivery_details=data("details"),
                                        delivery_type=data("delivery-type").upper(), delivery_image=image,
                                        delivery_weight=str(float(data("weight")) / 1000), receiver_name=data("name"),
                                        receiver_address=data("address"), receiver_contact=data("contact"),
                                        receiver_pin_code=data("pincode"))
        print(order)
        if order is not None:
            return redirect("confirmdelivery", pk=order.id)

def cancel_delivery(request,id):
    Delivery.objects.filter(id=id).update(current_status="Cancelled")
    user = request.user
    customer = UserDetails.objects.get(user=user)
    deliveries = Delivery.objects.filter(customer=customer)
    print(deliveries)
    return redirect("history")
    # return render(request, "history.html", {"data": deliveries})



def confirm_delivery(request, pk):
    if request.method == "GET":
        details = Delivery.objects.get(id=pk)
        print("de", details.delivery_weight)
        if details.delivery_type == "NORMAL":
            if float(details.delivery_weight) / 1000 < 1:
                amount = 50
                gst = 50 * 0.12
            else:
                amount = (float(details.delivery_weight) / 1000) * 50
                gst = (float(details.delivery_weight) / 1000) * 0.12
        else:
            if float(details.delivery_weight) / 1000 < 1:
                amount = 100
                gst = amount * 0.12
            else:
                amount = (float(details.delivery_weight) / 1000) * 100
                gst = (float(details.delivery_weight) / 1000) * 0.12
        Delivery.objects.filter(id=pk).update(delivery_price=amount + gst)
        return render(request, "confirmdelivery.html",
                      {"data": details, "amount": amount, "gst": gst, "total": amount + gst})

    if request.method == "POST":
        user = request.user
        id = request.POST.get("id")
        Delivery.objects.filter(id=id).update(payment_complete=True)
        my_email = settings.EMAIL_HOST_USER
        print(my_email)
        send_mail("Order sent for approval", "You have placed your order. You will be notified once it is approved",
                  my_email,
                  [user.email])
        return redirect("history")


def history(request):
    user = request.user
    customer = UserDetails.objects.get(user=user)
    print("USER=>", customer)
    deliveries = Delivery.objects.filter(customer=customer)
    print(deliveries)
    return render(request, "history.html", {"data": deliveries})


def html_to_pdf_view(request, id):
    delivery = Delivery.objects.get(id=id)
    html_string = render_to_string('pdf_template.html', {'delivery': delivery})

    html = HTML(string=html_string)
    html.write_pdf(target='./mypdf.pdf');

    fs = FileSystemStorage('')
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
        return response

    return response

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


class Feedback_(View):
    def get(self,*args,**kwargs):
        return render(self.request,"feedback.html")


    def post(self,*args,**kwargs):
        data = self.request.POST.get
        delivery = Delivery.objects.get(id=kwargs["id"])
        if Feedback.objects.filter(delivery=delivery).exists():
            Feedback.objects.filter(delivery=delivery).update(rating=data("rating"),review=data("review"))
            return redirect("history")
        Feedback.objects.update_or_create(delivery=delivery,delivery_person=delivery.delivery_person,customer=delivery.customer,rating=data("rating"),review=data("review"))
        return redirect("history")
