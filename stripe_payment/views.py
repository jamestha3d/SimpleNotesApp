from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from notes.models import PaymentMethod, User
from notes.serializers import PaymentMethodSerializer
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from simplenote import settings
import stripe
from .models import StripeCustomer
import json
# Create your views here.

class HomeView(ModelViewSet):
    pass

def index(request):
    return render(request, "stripe_payment/index.html")

class PaymentView(ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = []
    queryset = PaymentMethod.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request):
        #return Response(self.serializer_class(self.queryset, many=True).data)
        #return Response(PaymentMethodSerializer(PaymentMethod.objects.all(), many=True).data)
        pass

    @action(
        detail=False,
        methods=['GET', 'POST', 'PATCH',],
        permission_classes=(AllowAny,)
        )
    def payments(self, request):
        
        if request.method == 'GET':
            return Response(PaymentMethodSerializer(PaymentMethod.objects.all(), many=True).data)
        
        elif request.method == 'POST':
            stripe.api_key = settings.STRIPE_API_KEY
            pm = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": "4242424242424242",
                    "exp_month": 8,
                    "exp_year": 2029,
                    "cvc": "314",
                },
                )
            data = request.data
            user = request.user
            payment = PaymentMethod.objects.create(user=user, payment_json=json.dumps(pm["card"]), payment_id=pm["id"])
            return Response(PaymentMethodSerializer(payment).data)
    
    @action(
        detail=False,
        methods=['GET', 'POST', 'PATCH',],
        permission_classes=(AllowAny,)
        )
    def customers(self, request):
        stripe.api_key = settings.STRIPE_API_KEY
        user = request.user
        data = request.data
        if request.method == 'POST':

            customer = stripe.Customer.create(
                description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
                email = user.email,
                name = f"{user.username}"
                )
            pm = PaymentMethod.objects.filter(user=user).first() 
            if pm is not None:
                stripe.PaymentMethod.attach(
                    pm.payment_id,
                    customer.id
                )
            StripeCustomer.objects.filter(email=user.email)
            return Response(customer)

    @action(
        detail=False,
        methods=['GET', 'POST', 'PATCH',],
        permission_classes=(AllowAny,)
        )
    def attach(self, request):
        payment = request.data.get("paymentid")
        customer = request.data.get("customerid")
        stripe.api_key = settings.STRIPE_API_KEY
        attach = stripe.PaymentMethod.attach(
            payment, 
            customer = customer
        )
        return Response(attach)