from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
from .models import Client, Measurement, Order, Reminder, Payment
from .forms import MeasurementForm, OrderForm
from django import forms
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'note']



@login_required
def order_details_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, client__user=request.user)
    payments = order.payments.all().order_by('-payment_date')
    total_paid = sum(p.amount for p in payments)
    balance = float(order.price) - float(total_paid)
    if total_paid >= order.price:
        payment_status = 'Paid'
    elif total_paid > 0:
        payment_status = 'Part-paid'
    else:
        payment_status = 'Unpaid'
    today = timezone.now().date()
    order.is_overdue = order.due_date < today and order.delivery_status != 'completed'

    template = get_template('order_details_pdf.html')
    html = template.render({
        'order': order,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
        'payment_status': payment_status,
        'user': request.user,
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}_details.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with PDF generation')
    return response



# Create your views here.

def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else: messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login') 




def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([first_name, last_name, username, email, password]):
            messages.error(request, "All fields are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            messages.success(request, "Registration successful!")
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html')

@login_required
def dashboard(request):
    # Client stats
    total_clients = Client.objects.filter(user=request.user).count()
    new_clients_this_month = Client.objects.filter(
        user=request.user,
        date_added__month=datetime.now().month
    ).count()
    
    # Order stats
    active_orders = Order.objects.filter(client__user=request.user, delivery_status='pending').count()
    completed_orders = Order.objects.filter(client__user=request.user, delivery_status='completed').count()
    orders_change = 0  # Calculate percentage change from last month
    
    # Revenue stats
    # Total order value for the month
    monthly_order_value = Order.objects.filter(
        client__user=request.user,
        created_at__month=datetime.now().month
    ).aggregate(Sum('price'))['price__sum'] or 0

    # Payments received for the month
    monthly_revenue = Payment.objects.filter(
        order__client__user=request.user,
        payment_date__month=datetime.now().month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Upcoming deliveries
    upcoming_deliveries = Order.objects.filter(
        client__user=request.user,
        due_date__range=[datetime.now(), datetime.now() + timedelta(days=7)]
    ).count()
    
    # Recent data
    recent_orders = Order.objects.filter(client__user=request.user).order_by('-created_at')[:5]
    upcoming_orders = Order.objects.filter(
        client__user=request.user,
        delivery_status='pending'
    ).order_by('due_date')[:5]
    recent_clients = Client.objects.filter(user=request.user).order_by('-date_added')[:4]
    
    # Chart data
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    order_counts = [Order.objects.filter(
        client__user=request.user,
        created_at__month=i+1
    ).count() for i in range(12)]
    
    gender_distribution = [
        Client.objects.filter(user=request.user, gender='Male').count(),
        Client.objects.filter(user=request.user, gender='Female').count()
    ]
    
    return render(request, 'dashboard.html', {
        'total_clients': total_clients,
        'new_clients_this_month': new_clients_this_month,
        'active_orders': active_orders,
        'orders_change': orders_change,
        'monthly_revenue': monthly_revenue,
        'monthly_order_value': monthly_order_value,
        'upcoming_deliveries': upcoming_deliveries,
        'recent_orders': recent_orders,
        'upcoming_orders': upcoming_orders,
        'recent_clients': recent_clients,
        'month_labels': month_labels,
        'order_counts': order_counts,
        'gender_distribution': gender_distribution,
    })

@login_required
def add_client(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        gender = request.POST.get('gender', '').strip()
        if not name or not phone or not gender:
            messages.error(request, "Name, phone, gender are required.")
        else:
            user = request.user
            client = Client.objects.create(
                user=user,
                name=name,
                phone=phone,
                address=address,
                gender=gender
            )
            messages.success(request, "Client added successfully!")
            return redirect('client_profile', client_id=client.id)
    return render(request, 'add_client.html')

@login_required
def client_profile(request, client_id):
    client = get_object_or_404(Client, id=client_id, user=request.user)
    client_measurements = Measurement.objects.filter(client=client).first()
    # Calculate client statistics
    total_orders = Order.objects.filter(client=client).count()
    active_orders = Order.objects.filter(client=client, delivery_status='pending').count()
    total_spent = Order.objects.filter(client=client).aggregate(Sum('price'))['price__sum']
    return render(request, 'client_profile.html', {
        'client': client,
        'measurements': client_measurements,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'total_spent': total_spent,
    })

@login_required
def list_clients(request):
    query = request.GET.get('q', '').strip()
    clients = Client.objects.filter(user=request.user)
    if query:
        clients = clients.filter(
            name__icontains=query
        ) | clients.filter(
            phone__icontains=query
        )
        clients = clients.distinct()
    clients = clients.order_by('name')
    return render(request, 'list_clients.html', {'clients': clients, 'query': query})

@login_required
def list_orders(request):
    orders = Order.objects.filter(client__user=request.user).all()
    # Annotate each order with payment info
    for order in orders:
        order.total_paid = sum(p.amount for p in order.payments.all())
        order.balance = float(order.price) - float(order.total_paid)
        if order.total_paid >= order.price:
            order.payment_status = 'Paid'
        elif order.total_paid > 0:
            order.payment_status = 'Part-paid'
        else:
            order.payment_status = 'Unpaid'
    return render(request, 'list_orders.html', {'orders': orders})

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, client__user=request.user)
    payments = order.payments.all().order_by('-payment_date')
    total_paid = sum(p.amount for p in payments)
    balance = float(order.price) - float(total_paid)
    
    if total_paid >= order.price:
        payment_status = 'Paid'
    elif total_paid > 0:
        payment_status = 'Part-paid'
    else:
        payment_status = 'Unpaid'
    
    # Check if order is overdue
    today = timezone.now().date()
    order.is_overdue = order.due_date < today and order.delivery_status != 'completed'

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        print(form)
        if form.is_valid():
            print("here")
            payment = form.save(commit=False)
            payment.order = order
            payment.save()
            messages.success(request, 'Payment added successfully!')
            return redirect('order_details', order_id=order.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentForm()

    return render(request, 'order_details.html', {
        'order': order,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
        'payment_status': payment_status,
        'form': form,
    })

@login_required
def add_measurements(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    try:
        measurement = Measurement.objects.get(client=client)
    except Measurement.DoesNotExist:
        measurement = None

    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Measurements saved successfully.')
            return redirect('client_profile', client_id=client.id)
    else:
        form = MeasurementForm(instance=measurement)
        form.fields['client'].initial = client

    return render(request, 'add_measurements.html', {'form': form, 'client': client})

@login_required
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)  # Pass user here
        if form.is_valid():
            order = form.save(commit=False)
            order.save()
            messages.success(request, 'Order saved successfully.')
            return redirect('list_orders')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm(user=request.user)  # And here for GET requests

    return render(request, 'add_order.html', {'form': form})


@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, client__user=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('delivery_status')
        print("Received new status:", new_status)
        if new_status in ['pending', 'completed']:
            order.delivery_status = new_status
            order.save()
            messages.success(request, f"Order status updated to '{new_status}'")
        else:
            messages.error(request, "Invalid delivery status")
        return redirect('list_orders')  # Update this to your actual order list URL name
    else:
        messages.error(request, "Invalid request")
        return redirect('list_orders')


@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, "Order deleted successfully!")
    return redirect('list_orders')


# def list_payments(request):
#     payments = Payment.objects.filter(order__client__user=request.user).order_by('-payment_date')
#     return render(request, 'list_payments.html', {'payments': payments})

# def add_payment(request):
#     # Only show orders belonging to the logged-in user
#     user_orders = Order.objects.filter(client__user=request.user)
#     class UserPaymentForm(PaymentForm):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.fields['order'].queryset = user_orders
#     if request.method == 'POST':
#         form = UserPaymentForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Payment added successfully!")
#             return redirect('list_payments')
#         else:
#             messages.error(request, "There was an error with the form.")
#     else:
#         form = UserPaymentForm()
#     return render(request, 'add_payment.html', {'form': form})
