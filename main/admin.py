from django.contrib import admin

# Register your models here.

from .models import Client, Measurement, Order, Payment

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'gender', 'date_added')
    search_fields = ('name', 'phone')
    list_filter = ('date_added',)

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('client', 'bust', 'waist', 'hips', 'shoulder', 'sleeve_length', 'top_length', 'trouser_length', 'neck', 'updated_at')
    search_fields = ('client__name',)
    list_filter = ('updated_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('client', 'get_user', 'style_name', 'fabric_type', 'price', 'due_date', 'delivery_status', 'created_at')
    search_fields = ('client__name', 'style_name', 'fabric_type')
    list_filter = ('delivery_status', 'due_date', 'created_at')

    def get_user(self, obj):
        return obj.client.user
    get_user.short_description = 'User'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_date', 'method', 'note')
    search_fields = ('order__client__name', 'method')
    list_filter = ('payment_date', 'method')