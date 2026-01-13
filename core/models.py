from django.db import models
from django.contrib.auth.models import User


# -------------------- ACCOUNTS --------------------

class OTP(models.Model):
    mobile = models.CharField(max_length=10, db_index=True)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mobile} - {self.otp}"


# -------------------- TURFS --------------------

class Turf(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    price_per_hour = models.IntegerField()

    def __str__(self):
        return self.name


class Ground(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name="grounds")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.turf.name} - {self.name}"


class Slot(models.Model):
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE, related_name="slots")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


# -------------------- BOOKINGS --------------------

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"Cart - {self.user.username}"


class Booking(models.Model):
    BOOKING_STATUS = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.status}"


# -------------------- PAYMENTS --------------------

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=300, null=True, blank=True)

    amount = models.IntegerField()  # in paise
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.booking.id} - {self.status}"
