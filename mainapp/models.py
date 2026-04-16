from django.db import models
from decimal import Decimal

class Party(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Transaction(models.Model):

    TRANSACTION_TYPE = (
        ('credit', 'Credit'),  # paisa lena hai
        ('debit', 'Debit'),    # paisa aa gaya
    )

    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255, blank=True, null=True)

    reference_id = models.IntegerField(blank=True, null=True)  # 🔥 link with sale

    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        # 🔥 balance update
        if is_new:
            if self.type == 'credit':
                self.party.balance += self.amount
            else:
                self.party.balance -= self.amount

            self.party.save()


# Create your models here.
class Purchase(models.Model):
    supplier_name = models.CharField(max_length=255)
    vehicle_number = models.CharField(max_length=50)

    weight = models.FloatField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = Decimal(self.weight) * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier_name} ({self.vehicle_number})"

class Processing(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)

    rait = models.FloatField()
    bajri = models.FloatField()
    bajerkut = models.FloatField()

    date = models.DateField(auto_now_add=True)

class Sale(models.Model):

    # 🔥 PRODUCT
    PRODUCT_CHOICES = (
        ('rait', 'Rait'),
        ('bajri', 'Bajri'),
        ('bajerkut', 'Bajerkut'),
    )

    # 🔥 TRANSPORT TYPE
    TRANSPORT_TYPE = (
        ('customer', 'Customer Pay'),   # customer alag se dega
        ('included', 'Included'),       # rate me include
        ('free', 'Free'),               # tum bharoge
    )

    # 🔥 BASIC DETAILS
    party = models.ForeignKey('Party', on_delete=models.CASCADE)

    product = models.CharField(max_length=20, choices=PRODUCT_CHOICES)

    quantity = models.FloatField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5)

    # 🔥 TRANSPORT
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPE, default='customer')
    transport_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # 🔥 EXTRA INVOICE INFO
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    site_address = models.TextField(blank=True, null=True)

    # 🔥 TOTAL
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        # 🔥 1. AUTO INVOICE NUMBER
        if not self.invoice_number:
            last = Sale.objects.order_by('id').last()
            number = 1 if not last else last.id + 1
            self.invoice_number = f"INV-{number:04d}"

        # 🔥 2. CALCULATION
        self.subtotal = Decimal(self.quantity) * self.rate
        self.gst_amount = (self.subtotal * self.gst_percent) / 100

        # 🔥 3. TRANSPORT LOGIC
        if self.transport_type == 'customer':
            final_total = self.subtotal + self.gst_amount + self.transport_charge

        elif self.transport_type == 'included':
            final_total = self.subtotal + self.gst_amount

        elif self.transport_type == 'free':
            final_total = self.subtotal + self.gst_amount

        self.total_amount = final_total

        super().save(*args, **kwargs)

        # 🔥 4. AUTO TRANSACTION ENTRY
        if is_new:
            from .models import Transaction

            Transaction.objects.create(
                party=self.party,
                amount=self.total_amount,
                type='credit',
                description=f"Invoice {self.invoice_number} - {self.product}",
                reference_id=self.id
            )

    def __str__(self):
        return f"{self.invoice_number} - {self.party.name}"


class Employee(models.Model):

    EMPLOYEE_TYPE = (
        ('labour', 'Labour'),
        ('staff', 'Staff'),
        ('cook', 'Cook'),
    )

    SALARY_TYPE = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    )

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)

    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE)
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE)

    daily_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    food_deduction = models.BooleanField(default=True)
    food_rate = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    overtime_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Attendance(models.Model):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=(
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('leave', 'Leave'),          # unpaid leave
            ('paid_leave', 'Paid Leave'),# 🔥 add this
            ('half', 'Half Day'),    
            ('weekly_off', 'Weekly Off'),
        ),
        default='present'
    )
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # 🍛 Khana liya ya nahi
    took_food = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

class Salary(models.Model):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    month = models.IntegerField()
    year = models.IntegerField()

    total_days = models.IntegerField(default=0)
    present_days = models.FloatField(default=0)  # 🔥 float (half day ke liye)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    food_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    final_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.name}"
    
class DailyLabourPayment(models.Model):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    note = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.employee.employee_type != 'labour':
            raise ValueError("Only labour payment allowed")
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name} - {self.amount}"


class KitchenExpense(models.Model):

    date = models.DateField()

    description = models.CharField(max_length=255)  # chawal, sabji, tel etc.

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"
