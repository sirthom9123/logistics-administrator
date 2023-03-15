from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Measurement, AdditionalInfo, MyOffice

# TODO: PDF link for customers and style doc.
def export_invoice(obj):
    url = reverse('admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}" target="_blank">Export</a>')
export_invoice.short_description = "Export Invoice"

@admin.register(AdditionalInfo)
class AdditionalInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_code','first_name', 'last_name', 'pickup_date', 'created', export_invoice]
    list_filter = ['created',]
    search_fields = ['first_name', 'last_name'] 

admin.site.register(Measurement)
admin.site.register(MyOffice)
