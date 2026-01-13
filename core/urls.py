from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from core.views import (
    send_otp,
    verify_otp,
    signup,

    list_turfs,
    turf_details,
    ground_availability,

    add_to_cart,
    confirm_booking,

    create_payment_order,
    verify_payment,
)

urlpatterns = [

    # -------- AUTH --------
    path('auth/send-otp/', send_otp),
    path('auth/verify-otp/', verify_otp),
    path('auth/signup/', signup),
    path('auth/login/', TokenObtainPairView.as_view()),

    # -------- TURFS --------
    path('turfs/', list_turfs),
    path('turfs/<int:turf_id>/', turf_details),
    path('grounds/<int:ground_id>/availability/', ground_availability),

    # -------- BOOKINGS --------
    path('cart/add/', add_to_cart),
    path('booking/confirm/', confirm_booking),

    # -------- PAYMENTS --------
    path('payment/create-order/', create_payment_order),
    path('payment/verify/', verify_payment),
]
