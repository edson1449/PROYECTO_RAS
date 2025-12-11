from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from usuarios import views
from usuario import views as usuario_views
from django.conf import settings
from django.conf.urls.static import static 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_usuario, name='registro'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-funcionario/', views.panel_funcionario, name='panel_funcionario'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('centros/', views.centros_list, name='listar_centros'),
    path('coordinaciones/', views.coordinaciones_list, name='listar_coordinaciones'),
    path('usuarios/', usuario_views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', usuario_views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id>/', usuario_views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', usuario_views.eliminar_usuario, name='eliminar_usuario'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('carga-masiva/', views.carga_masiva_usuarios, name='carga_masiva'),
    path('ambientes/', include('ambientes.urls')),
    path('reservas/', include('reservas.urls')),
    path('centros-api/', include('centros.urls')),
    path('coordinaciones-api/', include('coordinaciones.urls')),
    path('historial-api/', include('historial.urls')),
    path('soporte/', include('soporte.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])