from django.urls import path
from . import views

app_name = 'centros'

urlpatterns = [
    path('', views.listar_centros, name='listar_centros'),
    path('crear/', views.crear_centro, name='crear_centro'),
    path('editar/<int:cod_centro>/', views.editar_centro, name='editar_centro'),
    path('eliminar/<int:cod_centro>/', views.eliminar_centro, name='eliminar_centro'),
]