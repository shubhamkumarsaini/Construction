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
    class Meta:
        model = Processing
        fields = ['purchase', 'rait', 'bajri', 'bajerkut']

        widgets = {
            'purchase': forms.Select(attrs={'class': 'form-control'}),
            'rait': forms.NumberInput(attrs={'class': 'form-control'}),
            'bajri': forms.NumberInput(attrs={'class': 'form-control'}),
            'bajerkut': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        purchase = cleaned_data.get('purchase')
        rait = cleaned_data.get('rait') or 0
        bajri = cleaned_data.get('bajri') or 0
        bajerkut = cleaned_data.get('bajerkut') or 0

        total = rait + bajri + bajerkut

        if purchase and total > purchase.weight:
            raise forms.ValidationError("Total processed quantity purchase se zyada nahi ho sakti")

        return cleaned_data
    
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

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # 🔥 YAHI LAGANA HAI
    def clean(self):
        cleaned_data = super().clean()

        salary_type = cleaned_data.get('salary_type')

        if salary_type == 'daily':
            cleaned_data['monthly_salary'] = 0

        elif salary_type == 'monthly':
            cleaned_data['daily_wage'] = 0

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
        }