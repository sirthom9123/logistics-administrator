from django.contrib import admin
from .models import Measurement, AdditionalInfo, MyOffice

@admin.register(AdditionalInfo)
class AdditionalInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_code','first_name', 'last_name', 'pickup_date', 'created']
    list_filter = ['created',]
    search_fields = ['first_name', 'last_name'] 

admin.site.register(Measurement)
admin.site.register(MyOffice)
