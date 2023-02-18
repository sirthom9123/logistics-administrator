# views.py
import requests, folium, os
from xhtml2pdf import pisa
from geopy.distance import distance as dt
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string, get_template
from django.contrib.staticfiles import finders
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

from .models import MyOffice, Measurement, AdditionalInfo
from .utils import get_zoom, get_center_coordinates
from .forms import CustomerForm


def orders_view(request):
    orders = AdditionalInfo.objects.all()
    office = MyOffice.objects.filter(pk=1).first()
    
    # Get distance and calculate cost
    # distance = orders.location.distance
    # cost = round(distance * int(office.cost_per_kilo), 2) 
    
    return render(request, 'map/orders.html', {'obj': orders})


def single_order(request, pk):
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
            'obj': obj,
            'total_cost': total_cost,
            'helper_cost': helper_cost, 
            'floors_cost': floors_cost,
            'cost': cost,
        }
    return render(request, 'map/order.html', context)
    

def index(request):
    pick_up = request.GET.get('pick_up')
    destination = request.GET.get('destination')
    map_html = ''
    tot_distance = ''
    cost = ''
    loc = ''
    form = CustomerForm()
    obj = get_object_or_404(MyOffice, id=1)
    
    if pick_up and destination:
        map_html, tot_distance = calculate_distance(pick_up, destination)
            
        # calculate the total cost for delivery
        cost = round(tot_distance * int(obj.cost_per_kilo), 2)

        # Create instance of request
        loc = Measurement.objects.create(
                    location=pick_up,
                    destination=destination,
                    distance=tot_distance
    )
    
    if loc:
        request.session['loc'] = loc.pk
        request.session['map'] = map_html
        request.session['distance'] = tot_distance
    else:
        request.session['loc'] = loc
        
        
    context = {
        'map_html': map_html,
        'distance': tot_distance,
        'cost': cost,
        'form': form
    }

    return render(request, 'map/tracker.html', context)

def calculate_distance(pick_up, destination):
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
    
    
    # Display the pick up and destination on a map using folium
    map = folium.Map(location=get_center_coordinates(l_lat, l_lon), zoom_start=13, tiles="cartodb positron")

    # Calculate Distance from the office to pick up
    distance_from_office = round(dt(pointA, my_office).km, 2)
    
    # Use the mapbox library to calculate the distance
    distance = round(dt(pointA, pointB).km, 2)
    
    # folium map modification
    map = folium.Map(location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
    
    # Pick up marker
    folium.Marker(location=[l_lat, l_lon], popup='Pick Up Location', icon=folium.Icon(color='purple')).add_to(map)
    
    # Destination marker
    folium.Marker(location=[d_lat, d_lon], popup='Destination', icon=folium.Icon(color='red')).add_to(map)
    
    # draw the line between location and destination
    line = folium.PolyLine(locations=[pointA, pointB], weight=5, color='blue')
    map.add_child(line)
    map_html = map._repr_html_()
    
    # Calculate total distance
    tot_distance = round(distance_from_office + distance, 2)
    

    return map_html, tot_distance

def get_coordinates(location):
    response = requests.get(f'https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={settings.MAPBOX_KEY}')
    data = response.json()
    coordinates = data['features'][0]['center']
    return coordinates


def customer_form(request):
    location = None
    if 'loc' in request.session:
        location = request.session['loc']
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
    
    
def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
            if not isinstance(result, (list, tuple)):
                    result = [result]
            result = list(os.path.realpath(path) for path in result)
            path=result[0]
    else:
            sUrl = settings.STATIC_URL        # Typically /static/
            sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
            mUrl = settings.MEDIA_URL         # Typically /media/
            mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

            if uri.startswith(mUrl):
                    path = os.path.join(mRoot, uri.replace(mUrl, ""))
            elif uri.startswith(sUrl):
                    path = os.path.join(sRoot, uri.replace(sUrl, ""))
            else:
                    return uri

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                    'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path


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