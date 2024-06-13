from django.forms import ModelForm
from django import forms
from .models import Locations, Incident, FireStation, Firefighters, FireTruck

class IncidentForm(ModelForm):
    class Meta:
        model = Incident
        fields = "__all__"

class LocationsForm(ModelForm):
    class Meta:
        model = Locations
        fields = "__all__"

class FireStationForm(ModelForm):
    class Meta:
        model = FireStation
        fields = "__all__"


class FirefighterForm(forms.ModelForm):
    class Meta:
        model = Firefighters
        fields = ['name', 'rank', 'experience_level', 'station']

class FireTruckForm(forms.ModelForm):
    class Meta:
        model = FireTruck
        fields = ['truck_number', 'model', 'capacity', 'station']