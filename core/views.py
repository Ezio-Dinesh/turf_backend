import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import (
    OTP,
    Cart,
    Booking,
    Payment,
    Turf,
    Ground,
    Slot
)

@api_view(['POST'])
def send_otp(request):
    mobile = request.data.get('mobile')
    if not mobile:
        return Response({"error": "Mobile required"}, status=400)

    OTP.objects.filter(mobile=mobile).delete()
    otp = str(random.randint(100000, 999999))
    OTP.objects.create(mobile=mobile, otp=otp)

    return Response({"message": "OTP sent"})

@api_view(['POST'])
def verify_otp(request):
    mobile = request.data.get('mobile')
    otp = request.data.get('otp')

    try:
        otp_obj = OTP.objects.get(
            mobile=mobile,
            otp=otp,
            created_at__gte=timezone.now() - timedelta(minutes=5),
            is_verified=False
        )
    except OTP.DoesNotExist:
        return Response({"error": "Invalid OTP"}, status=400)

    otp_obj.is_verified = True
    otp_obj.save()
    return Response({"message": "OTP verified"})

@api_view(['POST'])
def signup(request):
    mobile = request.data.get('mobile')
    password = request.data.get('password')

    if not password:
        return Response({"error": "Password required"}, status=400)

    if not OTP.objects.filter(mobile=mobile, is_verified=True).exists():
        return Response({"error": "OTP not verified"}, status=400)

    if User.objects.filter(username=mobile).exists():
        return Response({"error": "User already exists"}, status=400)

    User.objects.create(
        username=mobile,
        password=make_password(password)
    )

    OTP.objects.filter(mobile=mobile).update(is_verified=False)

    return Response({"message": "Account created successfully"})

@api_view(['GET'])
def list_turfs(request):
    return Response(list(Turf.objects.values()))

@api_view(['GET'])
def turf_details(request, turf_id):
    turf = Turf.objects.get(id=turf_id)
    return Response({
        "id": turf.id,
        "name": turf.name,
        "location": turf.location,
        "price_per_hour": turf.price_per_hour
    })

@api_view(['GET'])
def ground_availability(request, ground_id):
    slots = Slot.objects.filter(ground_id=ground_id, is_booked=False)
    return Response(list(slots.values()))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    Cart.objects.create(
        user=request.user,
        turf_id=request.data['turf_id'],
        ground_id=request.data['ground_id'],
        date=request.data['date'],
        slot_id=request.data['slot_id']
    )
    return Response({"message": "Added to cart"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_booking(request):
    cart = Cart.objects.get(
        id=request.data['cart_id'],
        user=request.user
    )

    booking = Booking.objects.create(
        user=request.user,
        cart=cart,
        status="CONFIRMED"
    )
    return Response({"booking_id": booking.id})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_order(request):
    booking = Booking.objects.get(id=request.data['booking_id'])

    payment = Payment.objects.create(
        user=request.user,
        booking=booking,
        razorpay_order_id="dummy_order_id",
        amount=request.data.get("amount", 50000),
        status="PENDING"
    )

    return Response({
        "order_id": payment.razorpay_order_id,
        "amount": payment.amount
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    payment = Payment.objects.get(
        razorpay_order_id=request.data['order_id']
    )
    payment.status = "SUCCESS"
    payment.save()

    return Response({"message": "Payment successful"})
