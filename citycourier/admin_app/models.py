from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class UserDetails(models.Model):
    USER_ROLES = (
        (u'SA', u'SA'),  # Super Admin
        (u'CA', u'CA'),  # Customer Admin
        (u'DP', u'DP'),  # Delivery Person
    )
    DELIVERY_PERSON_AVAILABILITY = ((u'AVAILABLE', u'AVAILABLE'), (u'BUSY', u'BUSY'))
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    delivery_person_availability = models.CharField(default="AVAILABLE", max_length=20,choices=DELIVERY_PERSON_AVAILABILITY)
    contact = models.CharField(max_length=10, null=True)
    address = models.TextField(max_length=100, null=True)
    pin_code = models.CharField(max_length=7, null=True)
    icon = models.ImageField(upload_to="images/", null=True)
    verification_doc = models.FileField(upload_to="documents/", null=True)
    payment_credentials = models.ImageField(upload_to="images/", null=True)
    role = models.CharField(choices=USER_ROLES, default="CA", max_length=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    is_verified=models.BooleanField(default=False,null=True)
    token = models.CharField(max_length=100, null=True)


class Delivery(models.Model):
    DELIVERY_CHOICES = ((u'NORMAL', u'NORMAL'), (u'FAST', u'FAST'))
    STATUS_CHOICES = (
        (u'Waiting', u'Waiting'),  # Waiting for approval
        (u'Accepted', u'Accepted'),  # Approved
        (u'Picked', u'Picked'),  # Picked Up
        (u'Delivered', u'Delivered'),  # Delivered
        (u'Cancelled', u'Cancelled'),  # Cancelled
    )
    delivery_person = models.ForeignKey(UserDetails, null=True, on_delete=models.CASCADE,related_name="Ddelivery_person")
    customer = models.ForeignKey(UserDetails, null=True, on_delete=models.CASCADE, related_name="Dcustomer")
    delivery_type = models.CharField(default="NORMAL", max_length=10, choices=DELIVERY_CHOICES)
    delivery_details = models.TextField(max_length=200, null=True)
    delivery_price = models.IntegerField(null=True)
    delivery_image = models.ImageField(upload_to="images/",null=True)
    delivery_weight = models.FloatField(null=True)
    delivered_time = models.TimeField(auto_now_add=True, null=True)
    delivered_date = models.DateField(auto_now_add=True, null=True)
    current_status = models.CharField(default="Waiting", max_length=10,choices=STATUS_CHOICES)
    receiver_name = models.CharField(max_length=20, null=True)
    receiver_address = models.TextField(max_length=100, null=True)
    receiver_pin_code = models.CharField(max_length=7, null=True)
    receiver_contact = models.CharField(max_length=10, null=True)
    payment_complete = models.BooleanField(default=False,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_completed = models.BooleanField(default=False, null=True)
    is_cancelled = models.BooleanField(default=False, null=True)


class Feedback(models.Model):
    delivery = models.ForeignKey(Delivery, null=True, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(UserDetails, null=True, on_delete=models.CASCADE,
                                        related_name="Fdelivery_person")
    customer = models.ForeignKey(UserDetails, null=True, on_delete=models.CASCADE, related_name="Fcustomer")
    rating = models.IntegerField(null=True)
    review = models.TextField(max_length=250, null=True)


class ResetPassword(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    token = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)