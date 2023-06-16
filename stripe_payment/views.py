from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
# Create your views here.

class HomeView(ModelViewSet):
    pass

def index(request):
    return render(request, "stripe_payment/index.html")