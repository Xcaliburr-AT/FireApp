from django.contrib import admin
from django.urls import path

from fireapp.views import dashboard, ChartView, pie_count_by_severity, line_count_by_month, bar_chart_data, fire_incidents_map, delete_location, IncidentList, IncidentCreateView, IncidentUpdateView, IncidentDeleteView, FirefighterListView, FirefighterCreateView, FirefighterUpdateView, FirefighterDeleteView, FireTruckListView, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView

from fireapp import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', dashboard, name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('pie_chart_data/', views.pie_count_by_severity, name='pie_chart_data'),
    path('line_chart_data/', views.line_count_by_month, name='line_chart_data'),
    path('bar_chart_data/', views.bar_chart_data, name='bar_chart_data'),
    path('stations', views.map_station, name='map-station'),
    path('fire_incidents_map/', views.fire_incidents_map, name='fire_incidents_map'),
    path('database/', views.database_view, name='database'),
    path('delete/<int:location_id>/', delete_location, name='delete_location'),

    path('firestation_list', IncidentList.as_view(), name='firestation-list'),
    path('firestation_list/add', IncidentCreateView.as_view(), name='firestation-add'),
    path('firestation_list/<pk>', IncidentUpdateView.as_view(), name='firestation-update'),
    path('firestation_list/<pk>/delete', IncidentDeleteView.as_view(), name='firestation-delete'),
    path('firefighter_list/', FirefighterListView.as_view(), name='firefighter-list'),
    path('firefighter/add/', FirefighterCreateView.as_view(), name='firefighter-add'),
    path('firefighter/<int:pk>/edit/', FirefighterUpdateView.as_view(), name='firefighter-edit'),
    path('firefighter/<int:pk>/delete/', FirefighterDeleteView.as_view(), name='firefighter-delete'),

    path('firetrucks/', FireTruckListView.as_view(), name='firetruck-list'),
    path('firetrucks/add/', FireTruckCreateView.as_view(), name='firetruck-add'),
    path('firetrucks/<int:pk>/', FireTruckUpdateView.as_view(), name='firetruck-edit'),
    path('firetrucks/<int:pk>/delete/', FireTruckDeleteView.as_view(), name='firetruck-delete'),

]