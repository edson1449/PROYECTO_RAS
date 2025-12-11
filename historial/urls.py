from django.urls import path
from . import views

app_name = 'historial' 

urlpatterns = [
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
]