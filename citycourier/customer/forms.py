from admin_app.models import Delivery
from django import forms


class DeliveryForm(forms.ModelForm):
    DELIVERY_CHOICES = ((u'NORMAL', u'NORMAL'), (u'FAST', u'FAST'))
    delivery_type = forms.ChoiceField(required=True,choices=DELIVERY_CHOICES)
    class Meta:
        model = Delivery

        exclude = ["delivery_person", "customer", "delivered_time", "delivered_date", "delivery_price",
                    "current_status","created_at", "is_completed", "is_cancelled","payment_complete"]
