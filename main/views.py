# views.py
from xhtml2pdf import pisa
from geopy.distance import distance as dt
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

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
    cost = round(distance * int(office.cost_per_kilo), 2) 
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
    print(map_html)
    
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
    pick_up = ''
    destination = ''
    map_html = ''
    map = ''
    tot_distance = ''
    cost = ''
    loc = ''
    form = CustomerForm()
    obj = get_object_or_404(MyOffice, id=1)
    token = settings.MAPBOX_KEY
    
    if request.method == 'POST':
        pick_up = request.POST.get('pick_up')
        destination = request.POST.get('destination')
        if pick_up and destination:
            map_html, tot_distance = calculate_distance(pick_up, destination)
                
            map = map_html._repr_html_()
            # calculate the total cost for delivery
            cost = round(tot_distance * int(obj.cost_per_kilo), 2)

            # get instance of calculate_distance helper
            loc = Measurement.objects.filter(
                        location=pick_up,
                        destination=destination,
                        distance=tot_distance
                    ).first()
        else:
            messages.error(request, 'Please enter both Pick-up and destination addresses!')
    
    
    
    if loc:
        request.session['loc'] = loc.pk
        request.session['map'] = map
        request.session['distance'] = tot_distance
    else:
        request.session['loc'] = loc
        
        
    context = {
        'map_html': map,
        'distance': tot_distance,
        'cost': cost,
        'form': form,
        'token': token,
        'destination': destination,
        'location': pick_up,
    }

    return render(request, 'map/index.html', context)

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
        
    print(location)
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.location_id = location
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
        cost = round(distance * int(obj.cost_per_kilo), 2) 
    
    
    customer = AdditionalInfo.objects.filter(location=location).first()
    
    if int(customer.additional_helpers) != 0:
        helper_cost = round(140 * int(customer.additional_helpers), 2)
    
    if int(customer.floors) != 0:
        floors_cost = round(int(customer.floors) * 80, 2)
        

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
        'distance' : distance,
        'destination': location,
        'map': map,
        'total_cost': total_cost,
        'helper_cost': helper_cost, 
        'floors_cost': floors_cost,
        'cost': cost,
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