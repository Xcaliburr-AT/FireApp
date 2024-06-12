from django.forms import CharField
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from fireapp.models import Locations, Incident, FireStation, Firefighters

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from fireapp.forms import IncidentForm, FireStationForm, FirefighterForm

from django.urls import reverse_lazy

from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
import calendar

from django.db.models import Count
from datetime import datetime


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"


def delete_location(request, location_id):
    # Fetch the location object
    location = get_object_or_404(Locations, id=location_id)
    
    if request.method == 'POST':
        # If form is submitted, delete the location
        location.delete()
        return redirect('database')  # Redirect to database page after deletion
    
    return render(request, 'del_location.html', {'location': location})


class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add additional context if needed
        return context

    def get_queryset(self, *args, **kwargs):
        # Return an empty queryset as this is a chart view
        return Incident.objects.none()


def pie_count_by_severity(request):
    incidents = Incident.objects.values('severity_level').annotate(count=Count('severity_level'))

    data = {incident['severity_level']: incident['count'] for incident in incidents}

    return JsonResponse(data)


def line_count_by_month(request):
    current_year = datetime.now().year
    incidents = Incident.objects.filter(date_time__year=current_year) \
                                .annotate(month=ExtractMonth('date_time')) \
                                .values('month') \
                                .annotate(count=Count('id')) \
                                .order_by('month')

    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {month_names[item['month']]: item['count'] for item in incidents}

    return JsonResponse(result_with_month_names)


def bar_chart_data(request):
    # Get the current year
    current_year = datetime.now().year

    # Fetch the data grouped by month
    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .annotate(month=ExtractMonth('date_time')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')

    # Create a dictionary with all months initialized to 0
    data = {calendar.month_abbr[i]: 0 for i in range(1, 13)}

    # Populate the data with the actual counts
    for item in incidents_per_month:
        month_name = calendar.month_abbr[item['month']]
        data[month_name] = item['count']

    return JsonResponse(data)


def CustomChart(request):
    # Custom chart logic, e.g., displaying top 3 countries by number of incidents
    query = '''
        SELECT 
        fl.country,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    GROUP BY 
        fl.country
    ORDER BY 
        incident_count DESC
    LIMIT 3;
    '''
    
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        data = {country: count for country, count in rows}
    else:
        data = {}

    return JsonResponse(data)

def map_station(request):
     fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

     for fs in fireStations:
         fs['latitude'] = float(fs['latitude'])
         fs['longitude'] = float(fs['longitude'])

     fireStations_list = list(fireStations)

     context = {
         'fireStations': fireStations_list,
     }

     return render(request, 'map_station.html', context)


def fire_incidents_map(request):
    locations_with_incidents = Locations.objects.annotate(
        num_incidents=Count('incident')
    ).values(
        'id', 'name', 'latitude', 'longitude', 'city', 'num_incidents'
    )

    # Convert latitude and longitude to float
    for location in locations_with_incidents:
        location['latitude'] = float(location['latitude'])
        location['longitude'] = float(location['longitude'])

    context = {
        'locations': list(locations_with_incidents),
    }

    return render(request, 'fire_incidents_map.html', context)



def database_view(request):
    # Querying all locations and incidents from the database
    locations = Locations.objects.all()
    incidents = Incident.objects.all()
    
    # Passing data to the template for rendering
    context = {
        'locations': locations,
        'incidents': incidents,
    }
    return render(request, 'database.html', context)


class IncidentList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = 'firestation/firestation_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(IncidentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q (address__icontains=query) |
                        Q (city__icontains=query) |
                        Q (country__icontains=query))
        return qs


class IncidentCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_add.html'
    success_url = reverse_lazy('firestation-list')


class IncidentUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_edit.html'
    success_url = reverse_lazy('firestation-list')


class IncidentDeleteView(DeleteView):
    model = FireStation
    template_name = 'firestation/firestation_del.html'
    success_url = reverse_lazy('firestation-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'ok'})
    

    
class FirefighterListView(ListView):
    model = Firefighters
    context_object_name = 'firefighters'
    template_name = 'firefighter/firefighter_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(FirefighterListView, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(rank__icontains=query) |
                Q(station__name__icontains=query)
            )
        return qs

class FirefighterCreateView(CreateView):
    model = Firefighters
    form_class = FirefighterForm
    template_name = 'firefighter/firefighter_add.html'
    success_url = reverse_lazy('firefighter-list')

class FirefighterUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefighterForm
    template_name = 'firefighter/firefighter_edit.html'
    success_url = reverse_lazy('firefighter-list')

class FirefighterDeleteView(DeleteView):
    model = Firefighters
    template_name = 'firefighter/firefighter_del.html'
    success_url = reverse_lazy('firefighter-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'ok'})