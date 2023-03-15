from django.contrib.gis.geoip2 import GeoIP2
import folium, requests, os
from django.conf import settings
from geopy.distance import distance as dt
from django.contrib.staticfiles import finders

# Helper functions
def get_coordinates(location):
    response = requests.get(f'https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={settings.MAPBOX_KEY}')
    data = response.json()
    coordinates = data['features'][0]['center']
    return coordinates

def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_geo(ip):
    g = GeoIP2()
    country = g.country(ip)
    city = g.city(ip)
    lat, lon = g.lat_lon(ip)
    return country, city, lat, lon

def get_center_coordinates(latA, longA, latB=None, longB=None):
    cord = (latA, longA)
    if latB:
        cord = [(latA+latB)/2, (longA+longB)/2]
    return cord

def get_zoom(distance):
    if distance <=100:
        return 8
    elif distance > 100 and distance <= 5000:
        return 4
    else:
        return 2
    

def get_map_rep(l_lat, l_lon, d_lat, d_lon):
    pointA = (l_lat, l_lon)
    pointB = (d_lat, d_lon)
    
    # Display the pick up and destination on a map using folium
    map = folium.Map(location=get_center_coordinates(l_lat, l_lon), zoom_start=13, tiles="cartodb positron")
    
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
    
    
    return map, distance


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