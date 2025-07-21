# forms.py
from django import forms
from .models import Measurement, Client, Order, Reminder
import datetime

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['client', 'bust', 'waist', 'hips', 'shoulder', 'sleeve_length', 'top_length', 'trouser_length', 'neck']

    client = forms.ModelChoiceField(queryset=Client.objects.all(), empty_label="Select Client")



class OrderForm(forms.ModelForm):
    # Set date range from today to Dec 31, 2030
    today = datetime.date.today()
    last_day_2030 = datetime.date(2030, 12, 31)

    due_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': today.strftime('%Y-%m-%d'),
                'max': last_day_2030.strftime('%Y-%m-%d'),
            }
        )
    )

    class Meta:
        model = Order
        fields = [field.name for field in Order._meta.fields if field.name != 'created_at']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['client'].queryset = Client.objects.filter(user=user)
