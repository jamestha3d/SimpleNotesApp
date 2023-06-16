from . import views
from django.urls import path

urlpatterns = [
    #path("homepage/", views.homepage, name="notes_home"),
    path("", views.index, name="index"),
]