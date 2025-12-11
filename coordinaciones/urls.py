from django.urls import path
from . import views

app_name = 'coordinaciones'

urlpatterns = [
    path('', views.listar_coordinaciones, name='listar_coordinaciones'),
    path('crear/', views.crear_coordinacion, name='crear_coordinacion'),
    path('editar/<int:cod_coordinacion>/', views.editar_coordinacion, name='editar_coordinacion'),
    path('eliminar/<int:cod_coordinacion>/', views.eliminar_coordinacion, name='eliminar_coordinacion'),
]