from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_usuario, name='registro'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-funcionario/', views.panel_funcionario, name='panel_funcionario'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('centros/', views.centros_list, name='listar_centros'),
    path('coordinaciones/', views.coordinaciones_list, name='listar_coordinaciones'),
    path('usuarios/', views.usuarios_list, name='listar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('reportes/', views.reportes_view, name='reportes'),
    
]
