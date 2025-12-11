from django.urls import path
from . import views

app_name = 'usuario'

urlpatterns = [
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<str:id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<str:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]