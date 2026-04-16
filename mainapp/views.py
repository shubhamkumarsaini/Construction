from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.db.models import Sum, Q
from django.contrib import messages
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from django.db.models.functions import TruncMonth
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.core.paginator import Paginator
from collections import defaultdict
import calendar
from datetime import date

# Create your views here.
def homepage(request):
    return render(request, 'home.html')

# @login_required
# def dashboard(request):
#     # 🔥 TOTALS
#     total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
#     total_purchase = Purchase.objects.aggregate(total=Sum('total_amount'))['total'] or 0
#     profit = total_sales - total_purchase

#     # 🔥 RECEIVED & PENDING
#     total_received = Transaction.objects.filter(type='debit').aggregate(total=Sum('amount'))['total'] or 0
#     total_credit = Transaction.objects.filter(type='credit').aggregate(total=Sum('amount'))['total'] or 0
#     total_debit = Transaction.objects.filter(type='debit').aggregate(total=Sum('amount'))['total'] or 0

#     total_pending = total_credit - total_debit
    

#     # 🔥 TODAY
#     today = date.today()
#     today_sales = Sale.objects.filter(date=today).aggregate(total=Sum('total_amount'))['total'] or 0
#     today_purchase = Purchase.objects.filter(date=today).aggregate(total=Sum('total_amount'))['total'] or 0

#     # 🔥 STOCK
#     total = Processing.objects.aggregate(
#         rait=Sum('rait'),
#         bajri=Sum('bajri'),
#         bajerkut=Sum('bajerkut')
#     )

#     sold = Sale.objects.aggregate(
#         rait=Sum('quantity', filter=Q(product='rait')),
#         bajri=Sum('quantity', filter=Q(product='bajri')),
#         bajerkut=Sum('quantity', filter=Q(product='bajerkut'))
#     )

#     stock = {
#         'rait': (total['rait'] or 0) - (sold['rait'] or 0),
#         'bajri': (total['bajri'] or 0) - (sold['bajri'] or 0),
#         'bajerkut': (total['bajerkut'] or 0) - (sold['bajerkut'] or 0),
#     }

#     # 🔥 LOW STOCK ALERT (<100)
#     low_stock = []
#     for k, v in stock.items():
#         if v < 100:
#             low_stock.append((k, v))

#     # 🔥 TOP PENDING PARTIES
#     parties = Party.objects.order_by('-balance')[:5]

#     # 🔥 MONTHLY SALES
#     monthly_sales = (
#         Sale.objects
#         .annotate(month=TruncMonth('date'))
#         .values('month')
#         .annotate(total=Sum('total_amount'))
#         .order_by('month')
#     )

#     sales_labels = []
#     sales_data = []

#     for item in monthly_sales:
#         sales_labels.append(item['month'].strftime('%b'))
#         sales_data.append(float(item['total']))

#     # 🔥 MONTHLY PURCHASE
#     monthly_purchase = (
#         Purchase.objects
#         .annotate(month=TruncMonth('date'))
#         .values('month')
#         .annotate(total=Sum('total_amount'))
#         .order_by('month')
#     )

#     purchase_data = []
#     profit_data = []

#     for i in range(len(sales_data)):
#         s = sales_data[i]
#         p = float(monthly_purchase[i]['total']) if i < len(monthly_purchase) else 0

#         purchase_data.append(p)
#         profit_data.append(s - p)

#     context = {
#         'total_sales': total_sales,
#         'total_purchase': total_purchase,
#         'profit': profit,
#         'total_received': total_received,
#         'total_pending': total_pending,
#         'today_sales': today_sales,
#         'today_purchase': today_purchase,
#         'stock': stock,
#         'low_stock': low_stock,
#         'parties': parties,
#         'sales_labels': sales_labels,
#         'sales_data': sales_data,
#         'purchase_data': purchase_data,
#         'profit_data': profit_data,
#     }

#     return render(request, 'dashboard.html', context)

@login_required
def dashboard(request):

    today = date.today()

    # 🔥 FILTER (month/year)
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])

    # 🔥 TOTALS (MONTH BASED)
    total_sales = Sale.objects.filter(date__range=[start_date, end_date])\
        .aggregate(total=Sum('total_amount'))['total'] or 0

    total_purchase = Purchase.objects.filter(date__range=[start_date, end_date])\
        .aggregate(total=Sum('total_amount'))['total'] or 0

    # 🔥 RECEIVED & PENDING
    total_received = Transaction.objects.filter(
        type='debit', date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_credit = Transaction.objects.filter(
        type='credit', date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_debit = Transaction.objects.filter(
        type='debit', date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_pending = total_credit - total_debit

    # 🔥 LABOUR PAYMENT (MONTH)
    total_labour_paid = DailyLabourPayment.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 🔥 KITCHEN EXPENSE (MONTH)
    total_kitchen_expense = KitchenExpense.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 🔥 ✅ FINAL PROFIT (CORRECT)
    total_expense = total_purchase + total_labour_paid + total_kitchen_expense
    profit = total_sales - total_expense

    # 🔥 STOCK
    total = Processing.objects.aggregate(
        rait=Sum('rait'),
        bajri=Sum('bajri'),
        bajerkut=Sum('bajerkut')
    )

    sold = Sale.objects.aggregate(
        rait=Sum('quantity', filter=Q(product='rait')),
        bajri=Sum('quantity', filter=Q(product='bajri')),
        bajerkut=Sum('quantity', filter=Q(product='bajerkut'))
    )

    stock = {
        'rait': (total['rait'] or 0) - (sold['rait'] or 0),
        'bajri': (total['bajri'] or 0) - (sold['bajri'] or 0),
        'bajerkut': (total['bajerkut'] or 0) - (sold['bajerkut'] or 0),
    }

    # 🔥 LOW STOCK
    low_stock = [(k, v) for k, v in stock.items() if v < 100]

    # 🔥 PARTIES
    parties = Party.objects.order_by('-balance')[:5]

    # 🔥 CHART (same as before - overall)
    monthly_sales = (
        Sale.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    sales_labels = []
    sales_data = []

    for item in monthly_sales:
        sales_labels.append(item['month'].strftime('%b'))
        sales_data.append(float(item['total']))

    monthly_purchase = (
        Purchase.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    purchase_data = []
    profit_data = []

    for i in range(len(sales_data)):
        s = sales_data[i]
        p = float(monthly_purchase[i]['total']) if i < len(monthly_purchase) else 0
        purchase_data.append(p)
        profit_data.append(s - p)

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    context = {
        'month': month,
        'year': year,
        'months': months,

        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'profit': profit,
        'total_received': total_received,
        'total_pending': total_pending,

        'total_labour_paid': total_labour_paid,
        'total_kitchen_expense': total_kitchen_expense,

        'stock': stock,
        'low_stock': low_stock,
        'parties': parties,

        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'purchase_data': purchase_data,
        'profit_data': profit_data,
    }

    return render(request, 'dashboard.html', context)

@login_required
def add_purchase(request):
    if not request.user.is_authenticated:
        return redirect('login')

    form = PurchaseForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('purchase_list')

    return render(request, 'purchase/add_purchase.html', {
        'form': form
    })


@login_required
def purchase_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    purchases = Purchase.objects.all().order_by('-id')

    return render(request, 'purchase/purchase_list.html', {
        'purchases': purchases
    })

@login_required
def add_processing(request):
    if not request.user.is_authenticated:
        return redirect('login')

    form = ProcessingForm(request.POST or None)

    if form.is_valid():

        purchase = form.cleaned_data['purchase']

        # ❌ duplicate check
        if Processing.objects.filter(purchase=purchase).exists():
            messages.error(request, "Is purchase ka processing already ho chuka hai ❌")
        else:
            processing = form.save(commit=False)

            total_input = purchase.weight

            total_output = (
                processing.rait +
                processing.bajri +
                processing.bajerkut
            )

            # 🔥 validation
            if total_output > total_input:
                messages.error(request, "Total output purchase se zyada nahi ho sakta ❌")
            else:
                processing.save()
                messages.success(request, "Processing saved successfully ✅")
                return redirect('processing_list')

    return render(request, 'processing/add_processing.html', {
        'form': form
    })


@login_required
def processing_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    data = Processing.objects.select_related('purchase').order_by('-id')

    return render(request, 'processing/processing_list.html', {
        'data': data
    })

@login_required
def stock_view(request):
    total = Processing.objects.aggregate(
        rait=Sum('rait'),
        bajri=Sum('bajri'),
        bajerkut=Sum('bajerkut')
    )

    sold = Sale.objects.aggregate(
        rait=Sum('quantity', filter=models.Q(product='rait')),
        bajri=Sum('quantity', filter=models.Q(product='bajri')),
        bajerkut=Sum('quantity', filter=models.Q(product='bajerkut'))
    )

    stock = {
        'rait': (total['rait'] or 0) - (sold['rait'] or 0),
        'bajri': (total['bajri'] or 0) - (sold['bajri'] or 0),
        'bajerkut': (total['bajerkut'] or 0) - (sold['bajerkut'] or 0),
    }

    return render(request, 'stock/stock.html', {'stock': stock})


@login_required
def add_party(request):
    form = PartyForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('party_list')

    return render(request, 'party/add_party.html', {
        'form': form
    })


# 📋 List Party
@login_required
def party_list(request):
    parties = Party.objects.all().order_by('-id')

    return render(request, 'party/party_list.html', {
        'parties': parties
    })

def add_transaction(request):
    form = TransactionForm(request.POST or None)

    party_id = request.GET.get('party')
    sale_id = request.GET.get('sale')

    if party_id:
        form.fields['party'].initial = party_id

    if form.is_valid():
        obj = form.save(commit=False)

        if sale_id:
            obj.reference_id = sale_id
            obj.description = f"Payment for Invoice ID {sale_id}"

        obj.save()

        messages.success(request, "Payment saved successfully ✅")
        return redirect('party_list')

    return render(request, 'transaction/add_transaction.html', {
        'form': form
    })

@login_required
def transaction_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    data = Transaction.objects.select_related('party').order_by('-id')

    return render(request, 'transaction/transaction_list.html', {
        'data': data
    })


@login_required
def add_sale(request):

    form = SaleForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            sale = form.save(commit=False)

            # 🔥 Total Stock
            stock = Processing.objects.aggregate(
                total_rait=Sum('rait'),
                total_bajri=Sum('bajri'),
                total_bajerkut=Sum('bajerkut')
            )

            # 🔥 Sold Stock
            sold = Sale.objects.aggregate(
                sold_rait=Sum('quantity', filter=Q(product='rait')),
                sold_bajri=Sum('quantity', filter=Q(product='bajri')),
                sold_bajerkut=Sum('quantity', filter=Q(product='bajerkut'))
            )

            # 🔥 Available
            available = {
                'rait': (stock['total_rait'] or 0) - (sold['sold_rait'] or 0),
                'bajri': (stock['total_bajri'] or 0) - (sold['sold_bajri'] or 0),
                'bajerkut': (stock['total_bajerkut'] or 0) - (sold['sold_bajerkut'] or 0),
            }

            current_stock = available.get(sale.product, 0)

            # 🔥 Validation
            if sale.quantity > current_stock:
                messages.error(
                    request,
                    f"❌ {sale.product.upper()} stock available: {current_stock} Qtl"
                )
            else:
                sale.save()
                messages.success(request, f"✅ Sale {sale.invoice_number} created")
                return redirect('sale_list')

        else:
            messages.error(request, "❌ Form invalid, check all fields")

    return render(request, 'sales/add_sale.html', {'form': form})

def sale_list(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'sales/sale_list.html', {'sales': sales})

@login_required
def party_detail(request, pk):
    party = get_object_or_404(Party, id=pk)

    transactions = Transaction.objects.filter(party=party).order_by('date', 'id')

    running_balance = 0
    ledger = []

    total_credit = 0
    total_debit = 0

    for t in transactions:
        if t.type == 'credit':
            running_balance += t.amount
            total_credit += t.amount
        else:
            running_balance -= t.amount
            total_debit += t.amount

        ledger.append({
            'date': t.date,
            'type': t.type,
            'amount': t.amount,
            'description': t.description,
            'balance': running_balance
        })

    context = {
        'party': party,
        'ledger': ledger,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'final_balance': running_balance
    }

    return render(request, 'party/party_detail.html', context)

@login_required
def print_invoice(request, pk):
    sale = get_object_or_404(Sale, id=pk)

    return render(request, 'sales/invoice.html', {
        'sale': sale
    })

@login_required
def invoice_pdf(request, pk):
    sale = get_object_or_404(Sale, id=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{sale.invoice_number}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    # 🔥 Company
    elements.append(Paragraph("Shubham Construction", styles['Title']))
    elements.append(Spacer(1, 10))

    # 🔥 Invoice Info
    elements.append(Paragraph(f"Invoice No: {sale.invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {sale.date}", styles['Normal']))
    elements.append(Paragraph(f"Party: {sale.party.name}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {sale.party.phone}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # 🔥 Transport Text
    if sale.transport_type == 'customer':
        transport_text = f"₹ {sale.transport_charge}"
    elif sale.transport_type == 'included':
        transport_text = "Included"
    else:
        transport_text = "Free"

    # 🔥 Table
    data = [
        ['Product', 'Qty', 'Rate', 'Subtotal'],
        [
            sale.product,
            sale.quantity,
            f"₹ {sale.rate}",
            f"₹ {sale.subtotal}"
        ]
    ]

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    elements.append(table)

    # 🔥 Summary
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"GST ({sale.gst_percent}%): ₹ {sale.gst_amount}", styles['Normal']))
    elements.append(Paragraph(f"Transport: {transport_text}", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Grand Total: ₹ {sale.total_amount}", styles['Heading2']))

    doc.build(elements)

    return response

@login_required
def add_employee(request):

    form = EmployeeForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Employee added successfully ✅")
        return redirect('employee_list')

    return render(request, 'employee/add_employee.html', {
        'form': form
    })


@login_required
def employee_list(request):

    search = request.GET.get('search') or ''

    employees = Employee.objects.all().order_by('-id')

    # 🔍 SEARCH (name + phone + type)
    if search:
        employees = employees.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(employee_type__icontains=search)
        )

    # 🔥 PAGINATION
    paginator = Paginator(employees, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employee/employee_list.html', {
        'employees': page_obj,
        'search': search
    })

@login_required
def toggle_employee(request, id):
    emp = Employee.objects.get(id=id)
    emp.is_active = not emp.is_active
    emp.save()

    return redirect('employee_list')

@login_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, id=pk)

    form = EmployeeForm(request.POST or None, instance=employee)

    if form.is_valid():
        form.save()
        messages.success(request, "Employee updated successfully ✅")
        return redirect('employee_list')

    return render(request, 'employee/edit_employee.html', {
        'form': form
    })

@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, id=pk)

    employee.delete()
    messages.success(request, "Employee deleted successfully ❌")

    return redirect('employee_list')

@login_required
def add_attendance(request):

    # 🔥 DATE FIX
    selected_date = request.GET.get('date')
    if not selected_date:
        selected_date = date.today().strftime('%Y-%m-%d')

    employees = Employee.objects.filter(is_active=True)

    # 🔥 existing attendance
    attendance_data = Attendance.objects.filter(date=selected_date)
    attendance_dict = {a.employee_id: a for a in attendance_data}

    if request.method == "POST":
        selected_date = request.POST.get('date')

        for emp in employees:
            status = request.POST.get(f'status_{emp.id}')
            took_food = request.POST.get(f'food_{emp.id}') == 'on'
            overtime = request.POST.get(f'ot_{emp.id}') or 0

            # 🔥 convert OT
            try:
                overtime = float(overtime)
            except:
                overtime = 0

            # 🔥 RULE APPLY
            if status in ['absent', 'leave', 'weekly_off']:
                took_food = False
                overtime = 0   # ❗ no OT

            Attendance.objects.update_or_create(
                employee=emp,
                date=selected_date,
                defaults={
                    'status': status,
                    'took_food': took_food,
                    'overtime_hours': overtime
                }
            )

        messages.success(request, "Attendance saved successfully ✅")
        return redirect(f'/attendance/add/?date={selected_date}')

    return render(request, 'attendance/add_attendance.html', {
        'employees': employees,
        'selected_date': selected_date,
        'attendance_dict': attendance_dict
    })


@login_required
def attendance_list(request):

    search_name = request.GET.get('name')
    search_date = request.GET.get('date')

    data = Attendance.objects.select_related('employee').order_by('-date')

    # ❌ remove 'None' string
    if search_name and search_name != "None":
        data = data.filter(employee__name__icontains=search_name)

    if search_date and search_date != "None":
        data = data.filter(date=search_date)

    # 🔥 PAGINATION
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'attendance/attendance_list.html', {
        'data': page_obj,
        'search_name': search_name if search_name != "None" else "",
        'search_date': search_date if search_date != "None" else "",
    })



@login_required
def view_attendance(request):

    today = date.today()

    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    total_days = calendar.monthrange(year, month)[1]
    days = list(range(1, total_days + 1))

    employees = Employee.objects.filter(is_active=True)

    attendance = Attendance.objects.filter(
        date__year=year,
        date__month=month
    )

    # 🔥 attendance dict
    attendance_dict = {}
    for a in attendance:
        attendance_dict[(a.employee_id, a.date.day)] = a

    # 🔥 payment dict (IMPORTANT)
    payments = DailyLabourPayment.objects.filter(
        date__year=year,
        date__month=month
    )

    payment_dict = {}
    for p in payments:
        payment_dict[(p.employee_id, p.date.day)] = p

    # 🔥 summary
    attendance_summary = defaultdict(lambda: {'present': 0, 'food': 0, 'ot': 0})

    for a in attendance:

        if a.status == 'present':
            attendance_summary[a.employee_id]['present'] += 1

        elif a.status == 'half':
            attendance_summary[a.employee_id]['present'] += 0.5

        if a.took_food:
            attendance_summary[a.employee_id]['food'] += 1

        if a.employee.employee_type == 'labour':
            attendance_summary[a.employee_id]['ot'] += float(a.overtime_hours)

    context = {
        'employees': employees,
        'days': days,
        'attendance_dict': attendance_dict,
        'payment_dict': payment_dict,   # 🔥 add this
        'attendance_summary': dict(attendance_summary),
        'month': month,
        'year': year,
    }

    return render(request, 'attendance/view_attendance.html', context)

@login_required
def generate_salary(request):

    month = int(request.GET.get('month'))
    year = int(request.GET.get('year'))

    total_days = calendar.monthrange(year, month)[1]

    employees = Employee.objects.filter(is_active=True)

    attendance = Attendance.objects.filter(
        date__year=year,
        date__month=month
    )

    # 🔥 summary dict
    summary = defaultdict(lambda: {
        'present': 0,
        'absent': 0,
        'food': 0,
        'ot_hours': 0
    })

    # 🔥 attendance loop
    for a in attendance:

        # ✅ Present
        if a.status == 'present':
            summary[a.employee_id]['present'] += 1

        # ✅ Half day
        elif a.status == 'half':
            summary[a.employee_id]['present'] += 0.5

        # ❌ Absent / Unpaid Leave
        elif a.status in ['absent', 'leave']:
            summary[a.employee_id]['absent'] += 1

        # ✅ Paid Leave / Weekly Off (full pay)
        elif a.status in ['paid_leave', 'weekly_off']:
            summary[a.employee_id]['present'] += 1

        # 🍛 Food
        if a.took_food:
            summary[a.employee_id]['food'] += 1

        # ⏱ OT only labour
        if a.employee.employee_type == 'labour':
            summary[a.employee_id]['ot_hours'] += float(a.overtime_hours)

    # 🔥 salary save
    for emp in employees:

        data = summary.get(emp.id, {})

        present_days = Decimal(str(data.get('present', 0)))
        absent_days = Decimal(str(data.get('absent', 0)))
        food_count = data.get('food', 0)
        ot_hours = Decimal(str(data.get('ot_hours', 0)))

        # =========================
        # 💰 SALARY CALCULATION
        # =========================

        if emp.salary_type == 'daily':

            total_salary = present_days * emp.daily_wage

        else:
            per_day_salary = emp.monthly_salary / Decimal(str(total_days))

            deduction = absent_days * per_day_salary

            total_salary = emp.monthly_salary - deduction

        # =========================
        # ⏱ OT AMOUNT
        # =========================
        overtime_amount = ot_hours * emp.overtime_rate

        # =========================
        # 🍛 FOOD DEDUCTION
        # =========================
        if emp.food_deduction:
            food_deduction = food_count * emp.food_rate
        else:
            food_deduction = Decimal('0')

        # =========================
        # 💵 FINAL SALARY
        # =========================
        final_salary = total_salary + overtime_amount - food_deduction

        # =========================
        # 💾 SAVE
        # =========================
        Salary.objects.update_or_create(
            employee=emp,
            month=month,
            year=year,
            defaults={
                'total_days': total_days,
                'present_days': present_days,
                'overtime_amount': overtime_amount,
                'total_salary': total_salary,
                'food_deduction': food_deduction,
                'final_salary': final_salary
            }
        )

    messages.success(request, "Salary generated successfully ✅")

    return redirect(f'/salary/list/?month={month}&year={year}')

@login_required
def salary_list(request):

    today = date.today()

    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    month_names = [
        "January ", "February ", "March ", "April ", "May ", "June ",
        "July ", "August ", "September", " October", " November ", "December"
    ]

    employees = Employee.objects.filter(is_active=True)

    salary_qs = Salary.objects.filter(month=month, year=year)

    # 🔥 dict (employee_id -> salary)
    salary_dict = {s.employee_id: s for s in salary_qs}

    return render(request, 'salary/salary_list.html', {
        'employees': employees,
        'salary_dict': salary_dict,
        'month': month,
        'year': year,
        'month_names': month_names
    })


@login_required
def toggle_salary_status(request, id):

    salary = get_object_or_404(Salary, id=id)
    today = date.today()

    # ❌ current/future month block
    if (salary.year > today.year) or (
        salary.year == today.year and salary.month >= today.month
    ):
        messages.error(request, "❌ Current/Future month salary cannot be paid")
        return redirect(request.META.get('HTTP_REFERER', '/salary/list/'))

    # ❌ already paid → block
    if salary.is_paid:
        messages.warning(request, "⚠️ Salary already marked as Paid, cannot revert")
        return redirect(request.META.get('HTTP_REFERER', '/salary/list/'))

    # ✅ only unpaid → paid
    salary.is_paid = True
    salary.save()

    messages.success(request, "✅ Salary marked as Paid")

    return redirect(request.META.get('HTTP_REFERER', '/salary/list/'))

@login_required
def view_salary(request):

    today = date.today()

    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    employees = Employee.objects.filter(is_active=True)

    # 🔥 salary data
    salary_qs = Salary.objects.filter(month=month, year=year)

    # 🔥 dict बनाओ (employee_id -> salary)
    salary_dict = {s.employee_id: s for s in salary_qs}

    context = {
        'employees': employees,
        'salary_dict': salary_dict,
        'month': month,
        'year': year,
    }

    return render(request, 'salary/view_salary.html', context)


@login_required
def add_labour_payment(request, emp_id):

    employee = get_object_or_404(Employee, id=emp_id)

    # ❌ safety check
    if employee.employee_type != 'labour':
        messages.error(request, "Only labour payment allowed ❌")
        return redirect('/salary/list/')

    # ✅ default date (proper format)
    payment_date = request.GET.get('date')
    if not payment_date:
        payment_date = date.today().strftime('%Y-%m-%d')

    # ✅ default amount from employee
    default_amount = employee.daily_wage

    if request.method == "POST":
        payment_date = request.POST.get('date')
        amount = request.POST.get('amount')
        note = request.POST.get('note')

        DailyLabourPayment.objects.update_or_create(
            employee=employee,
            date=payment_date,
            defaults={
                'amount': Decimal(amount),
                'note': note
            }
        )

        messages.success(request, "Payment saved ✅")
        return redirect('/salary/list/')

    return render(request, 'salary/add_labour_payment.html', {
        'employee': employee,
        'date': payment_date,
        'amount': default_amount   # 🔥 pass default amount
    })

@login_required
def kitchen_expense(request):

    today = date.today()

    # 🔥 filter
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    expenses = KitchenExpense.objects.filter(
        date__month=month,
        date__year=year
    ).order_by('-date')

    # 🔥 total
    total_amount = sum(e.amount for e in expenses)

    # 🔥 ADD
    if request.method == "POST":
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        exp_date = request.POST.get('date') or today

        KitchenExpense.objects.create(
            description=description,
            amount=amount,
            date=exp_date
        )

        messages.success(request, "Expense added ✅")
        return redirect(f'/kitchen-expense/?month={month}&year={year}')

    return render(request, 'kitchen/expense.html', {
        'expenses': expenses,
        'month': month,
        'year': year,
        'today': today,
        'total_amount': total_amount
    })