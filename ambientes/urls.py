from django.urls import path
from . import views

app_name = 'ambientes'

urlpatterns = [
    path('', views.listar_ambientes, name='listar_ambientes'),
    path('ver/', views.listar_ambientes_funcionario, name='listar_ambientes_funcionario'),
    path('crear/', views.crear_ambiente, name='crear_ambiente'),
    path('editar/<int:cod_amb>/', views.editar_ambiente, name='editar_ambiente'),
    path('eliminar/<int:cod_amb>/', views.eliminar_ambiente, name='eliminar_ambiente'),
]
