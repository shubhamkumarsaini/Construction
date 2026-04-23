from django import forms
from .models import *

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier_name', 'vehicle_number', 'weight', 'rate']

        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'   # 🔥 decimal support
            }),
        }


class ProcessingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 already processed purchases निकालो
        processed_ids = Processing.objects.values_list('purchase_id', flat=True)

        # 🔥 सिर्फ unprocessed दिखाओ
        self.fields['purchase'].queryset = Purchase.objects.exclude(id__in=processed_ids)

    class Meta:
        model = Processing
        fields = ['purchase', 'rait', 'bajri', 'bajerkut']

        widgets = {
            'purchase': forms.Select(attrs={'class': 'form-control'}),
            'rait': forms.NumberInput(attrs={'class': 'form-control'}),
            'bajri': forms.NumberInput(attrs={'class': 'form-control'}),
            'bajerkut': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['name', 'phone', 'address']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['party', 'amount', 'type', 'description']

        widgets = {
            'party': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'party', 'product', 'quantity', 'rate',
            'gst_percent',
            'transport_type', 'transport_charge',
            'vehicle_number', 'site_address'
        ]

        widgets = {
            'party': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'gst_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'transport_type': forms.Select(attrs={'class': 'form-control'}),
            'transport_charge': forms.NumberInput(attrs={'class': 'form-control'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'site_address': forms.Textarea(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),

            'employee_type': forms.Select(attrs={'class': 'form-control'}),
            'salary_type': forms.Select(attrs={'class': 'form-control'}),

            'daily_wage': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_salary': forms.NumberInput(attrs={'class': 'form-control'}),

            'food_deduction': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'food_rate': forms.NumberInput(attrs={'class': 'form-control'}),

            # 🔥 NEW FIELD
            'overtime_rate': forms.NumberInput(attrs={'class': 'form-control'}),

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        salary_type = cleaned_data.get('salary_type')
        daily_wage = cleaned_data.get('daily_wage')
        monthly_salary = cleaned_data.get('monthly_salary')
        food_deduction = cleaned_data.get('food_deduction')
        food_rate = cleaned_data.get('food_rate')
        overtime_rate = cleaned_data.get('overtime_rate')

        # 🔥 Salary Logic
        if salary_type == 'daily':
            cleaned_data['monthly_salary'] = 0

            if not daily_wage or daily_wage <= 0:
                raise forms.ValidationError("Daily wage required")

        elif salary_type == 'monthly':
            cleaned_data['daily_wage'] = 0

            if not monthly_salary or monthly_salary <= 0:
                raise forms.ValidationError("Monthly salary required")

        # 🔥 Food Logic
        if food_deduction:
            if not food_rate or food_rate <= 0:
                raise forms.ValidationError("Food rate required")

        # 🔥 Overtime Logic (NEW)
        if overtime_rate is not None and overtime_rate < 0:
            raise forms.ValidationError("Overtime rate cannot be negative")

        return cleaned_data

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = '__all__'

        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'took_food': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control'}),  # 🔥 ADD
        }

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'

        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'present_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'food_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'final_salary': forms.NumberInput(attrs={'class': 'form-control'}),
        }