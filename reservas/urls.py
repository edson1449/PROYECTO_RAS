from django.urls import path
from . import views
from .views import reservas_json, enviar_correo_vista

app_name = 'reservas'

urlpatterns = [
    path('', views.listar_reservas, name='listar_reservas'),
    path('lista/', views.listar_reservas_tabla, name='listar_reservas_tabla'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('editar/<int:cod_reserva>/', views.editar_reserva, name='editar_reserva'),
    path('eliminar/<int:cod_reserva>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('reservas-json/', reservas_json, name='reservas_json'),
    path('detalles/<str:cod_reserva>/', views.detalles_reserva, name='detalles_reserva'),
    path('api/reservas/ambiente/<int:ambiente_id>/', views.reservas_por_ambiente, name='reservas_por_ambiente'),
    path('api/ambientes/disponibles/', views.ambientes_disponibles, name='ambientes_disponibles'),
    path('api/reservas/', views.obtener_reservas_api, name='obtener_reservas_api'),
    path('enviar-correo/<int:cod_reserva>/', enviar_correo_vista, name='enviar_correo'),
    path('api/calendario/', views.obtener_reservas_json, name='obtener_reservas_json'),
    path('cambiar-estado/<int:cod_reserva>/', views.cambiar_estado_reserva, name='cambiar_estado_reserva'),
    path('comentar-funcionario/<int:pk>/', views.comentar_reserva_funcionario, name='comentar_reserva_funcionario'),
    path('comentar-admin/<int:pk>/', views.comentar_reserva_admin, name='comentar_reserva_admin'),
    path('marcar-recibido/<int:cod_reserva>/', views.marcar_ambiente_recibido, name='marcar_ambiente_recibido'),
    
]
