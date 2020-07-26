"""citycourier URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import settings
from admin_app.views import *
from customer.views import *
from deliveryperson.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login",LoginForm.as_view(),name="login"),
    path("",home,name="home"),
    path("signup",SignupForm.as_view(),name="signup"),
    path("logout",logout_user,name="logout"),
    path("add-admin",add_admin,name="add-admin"),
    path("add-delivery-person",add_delivery_person,name="add-delivery-person"),
    path("adddelivery",AddDelivery.as_view(),name="adddelivery"),
    path("history",history,name="history"),
    path("confirmdelivery/<int:pk>",confirm_delivery,name="confirmdelivery"),
    path("orderaction",OrderAction.as_view(),name="orderaction"),
    path("mydeliveries",MyDeliveries.as_view(),name="mydeliveries"),
    path("html_to_pdf/<int:id>",html_to_pdf_view,name="html_to_pdf"),
    path("cancel-delivery/<int:id>",cancel_delivery,name="cancel-delivery"),
    path("reset_password",reset_password,name="reset_password"),
    path("resetpassword/<str:token>",ResetPasswordView.as_view(),name="resetpassword"),
    path("verify/<str:token>",verify_account,name="verify"),
    path("feedback/<int:id>",Feedback_.as_view(),name="feedback"),

] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
