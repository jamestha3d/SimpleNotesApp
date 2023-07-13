from .views import PaymentView, index
from django.urls import path, include, re_path
from django.urls import path
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register("payment", PaymentView, basename="payments")
urlpatterns = [
    #path("homepage/", views.homepage, name="notes_home"),
    path("home/", index, name="index"),
    path("", include(router.urls)),
]