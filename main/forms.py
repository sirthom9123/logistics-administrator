from django import forms
from .models import Measurement, AdditionalInfo
        

class CustomerForm(forms.ModelForm):
    class Meta:
        model = AdditionalInfo
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'additional_helpers', 'floors', 'pickup_date']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_helpers': forms.Select(attrs={'class': 'form-control'}),
            'floors': forms.TextInput(attrs={'class': 'form-control'}),
            'pickup_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields['pickup_date'].input_formats = ('%Y-%m-%dT%H:%M',)