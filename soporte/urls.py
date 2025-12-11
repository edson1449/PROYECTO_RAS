# soporte/urls.py

from django.urls import path
from . import views

app_name = 'soporte'

urlpatterns = [
    path('admin/soportes/', views.listar_soportes, name='listar_soportes'),
    path('admin/soportes/<int:soporte_id>/editar/', views.responder_soporte, name='responder_soporte'),
    path('admin/soportes/<int:soporte_id>/eliminar/', views.eliminar_soporte, name='eliminar_soporte'),
    path('detalle/<int:soporte_id>/', views.detalle_soporte, name='detalle_soporte'),
    path('crear/', views.crear_soporte, name='crear_soporte'),
    path('mis-soportes/', views.listar_mis_soportes, name='listar_mis_soportes'),
    path('detalle/<int:soporte_id>/', views.detalle_soporte, name='detalle_soporte'),
]
