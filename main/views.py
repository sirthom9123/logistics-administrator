# views.py
from xhtml2pdf import pisa
from geopy.distance import distance as dt
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from decimal import Decimal

from .models import MyOffice, Measurement, AdditionalInfo
from .utils import get_map_rep, get_coordinates, link_callback
from .forms import CustomerForm



def orders_view(request):
    if not request.user.is_staff:
        return redirect('/')
    orders = AdditionalInfo.objects.all()
    
    context = {'obj': orders}
    
    return render(request, 'map/orders.html', context)

def single_order(request, pk):
    if not request.user.is_staff:
        return redirect('/')
    floors_cost = None
    helper_cost = None
    
    office = MyOffice.objects.filter(pk=1).first()
    obj = AdditionalInfo.objects.filter(pk=pk).first()
    
    # Get distance and calculate cost
    distance = obj.location.distance
    cost = round((Decimal(distance) * Decimal(office.cost_per_kilo)) + Decimal(office.platform_fee), 2) 
    if int(obj.additional_helpers) != 0:
        helper_cost = round(140 * int(obj.additional_helpers), 2)
    
    if int(obj.floors) != 0:
        floors_cost = round(int(obj.floors) * 80, 2)
        
    # calculate costs
    total_cost = None
    if floors_cost == 0:
        total_cost = helper_cost + cost
    elif helper_cost == 0:
        total_cost = floors_cost + cost
    elif helper_cost != 0 and floors_cost != 0:
        total_cost = helper_cost + floors_cost + cost
    elif helper_cost == 0 and floors_cost == 0:
        total_cost = cost + 0
        
    # Get Map
    map, distance = get_map_rep(float(obj.location.l_lat), float(obj.location.l_lng), float(obj.location.d_lat), float(obj.location.d_lng))
    map_html = map._repr_html_()
    
    context = {
            'obj': obj,
            'total_cost': total_cost,
            'helper_cost': helper_cost, 
            'floors_cost': floors_cost,
            'cost': cost,
            'map': map_html,
        }
    return render(request, 'map/order.html', context)
    

def index(request):
    form = CustomerForm()
    token = settings.MAPBOX_KEY
        
        
    context = {
        'form': form,
        'token': token,
    }

    return render(request, 'map/index.html', context)


def cost_estimates(request):
    map_html = ''
    map = None
    tot_distance = ''
    data = {}
    obj = get_object_or_404(MyOffice, id=1)
    
    if request.method == 'GET':
        pick_up = request.GET.get('pick_up')
        destination = request.GET.get('destination')
        map_html, tot_distance = calculate_distance(pick_up, destination)
        
        map = map_html._repr_html_()
        # calculate the total cost for delivery
        cost = round((Decimal(tot_distance) * Decimal(obj.cost_per_kilo)) + Decimal(obj.platform_fee), 2)
            
        request.session['map'] = map
        
        data = {
            "destination": destination,
            "location": pick_up,
            "cost": float(cost),
        }
        
        loc = Measurement.objects.filter(
                    location=pick_up,
                    destination=destination
                ).first()  
        if loc:
            request.session['loc'] = loc.pk
            request.session['distance'] = tot_distance
        else:
            request.session['loc'] = loc
        
        return JsonResponse(data)

    
    
    

def calculate_distance(pick_up, destination):
    """Calculate the distance between the office, pick-up and drop-off and render map view"""
    # office location
    obj = get_object_or_404(MyOffice, id=1)
    office_lat = float(obj.lat)
    office_lng = float(obj.lng)
    my_office = (office_lat, office_lng)
    
    # Get the coordinates for the pick up and destination
    pick_up_coord = get_coordinates(pick_up)
    l_lat = pick_up_coord[1]
    l_lon = pick_up_coord[0]
    pointA = (l_lat, l_lon)
    
    destination_coord = get_coordinates(destination)
    d_lat = destination_coord[1]
    d_lon = destination_coord[0]
    pointB = (d_lat, d_lon)
    
    # Get map from helper function
    map_html, distance = get_map_rep(l_lat, l_lon, d_lat, d_lon)
    
    # Calculate distance from office to pick-up
    distance_from_office = round(dt(pointA, my_office).km, 2)
    
    # Calculate total distance
    tot_distance = round(distance_from_office + distance, 2)


    # Create instance of request
    Measurement.objects.create(
                location=pick_up,
                destination=destination,
                distance=tot_distance,
                l_lat=l_lat,
                l_lng=l_lon,
                d_lat=d_lat,
                d_lng=d_lon,
            )
    
    return map_html, tot_distance



def customer_form(request):
    location = None
    if 'loc' in request.session:
        location = request.session['loc']

    form = CustomerForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.location_id = location
        instance.paid = False
        instance.save()
        
        messages.success(request, "Request has been created!")
        return redirect('/complete_view/')
    else:
        messages.error(request, form.errors)
        return redirect('/')
    
def complete_view(request):
    location = None
    map = None
    distance = None
    cost = 0
    helper_cost = 0
    floors_cost = 0
    obj = get_object_or_404(MyOffice, id=1)
    
    
    if 'loc' in request.session:
        location = Measurement.objects.filter(pk=request.session['loc']).first()
        map = request.session['map']
        distance = request.session['distance']
        cost = round((distance * int(obj.cost_per_kilo)) + int(obj.platform_fee), 2) 
    
    
    customer = AdditionalInfo.objects.filter(location=location).first()
    
    if int(customer.additional_helpers) != 0:
        helper_cost = round(250 * int(customer.additional_helpers), 2)
    
    if int(customer.floors) != 0:
        floors_cost = round(int(customer.floors) * 50, 2)
        

    total_cost = None
    if floors_cost == 0:
        total_cost = helper_cost + cost
    elif helper_cost == 0:
        total_cost = floors_cost + cost
    elif helper_cost != 0 and floors_cost != 0:
        total_cost = helper_cost + floors_cost + cost
    elif helper_cost == 0 and floors_cost == 0:
        total_cost = cost + 0

    request.session['cost'] = cost
    request.session['total_cost'] = total_cost
    request.session['helper_cost'] = helper_cost
    request.session['floors_cost'] = floors_cost
    
    context = {
        'map': map,
        'distance' : distance,
        'destination': location,
        'total_cost': float(total_cost),
        'helper_cost': float(helper_cost), 
        'floors_cost': float(floors_cost),
        'cost': float(cost),
        'user': customer,
    }
    
    return render(request, 'map/complete.html', context)


def export_quote(request, id):
    instance = get_object_or_404(AdditionalInfo, id=id)
    location = Measurement.objects.filter(pk=request.session['loc']).first()
    obj = get_object_or_404(MyOffice, id=1)
    cost = request.session['cost']
    total_cost = request.session['total_cost']
    helper_cost = request.session['helper_cost'] 
    floors_cost = request.session['floors_cost'] 

    context = {
            'user': instance, 
            'destination': location,
            'total_cost': total_cost,
            'cost': cost,
            'helper_cost': helper_cost, 
            'floors_cost': floors_cost,
            'rate': obj.cost_per_kilo
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=quotation_{instance.customer_code}.pdf'
    template = get_template('pdf.html')
    html = template.render(context) 
    
    # create pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@staff_member_required
def admin_order_pdf(request, order_id):
    customer_obj = get_object_or_404(AdditionalInfo, id=order_id)
    office_obj = get_object_or_404(MyOffice, id=1)
    
    distance = None
    cost = 0
    helper_cost = 0
    floors_cost = 0
    
    cost = round((customer_obj.location.distance * int(office_obj.cost_per_kilo)) + int(office_obj.platform_fee), 2) 
    
    if int(customer_obj.additional_helpers) != 0:
        helper_cost = round(250 * int(customer_obj.additional_helpers), 2)
    
    if int(customer_obj.floors) != 0:
        floors_cost = round(int(customer_obj.floors) * 50, 2)
    
    total_cost = None
    if floors_cost == 0:
        total_cost = helper_cost + cost
    elif helper_cost == 0:
        total_cost = floors_cost + cost
    elif helper_cost != 0 and floors_cost != 0:
        total_cost = helper_cost + floors_cost + cost
    elif helper_cost == 0 and floors_cost == 0:
        total_cost = cost + 0
    
    context = {
            'user': customer_obj, 
            'destination': customer_obj.location,
            'total_cost': total_cost,
            'cost': cost,
            'helper_cost': helper_cost, 
            'floors_cost': floors_cost,
            'rate': office_obj.cost_per_kilo
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=quotation_{customer_obj.customer_code}.pdf'
    template = get_template('pdf.html')
    html = template.render(context) 
    pdf_encoding='UTF-8'
    
    # create pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback, encoding=pdf_encoding)
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response