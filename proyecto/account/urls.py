from django.urls import path
from . import views, api_views
urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login_view,name='login'),
    path('registro/',views.registro,name='registro'),
    path("registroAdmin/", views.registroAdmin, name="registroAdmin"),
    path('employee/', views.employee, name='employee'),
    path('employee_inicio/', views.employee_inicio, name='employee_inicio'),
    path('listar_datos_cuidador/', views.listar_datos_cuidador, name='listar_datos_cuidador'),
    path('registro_datos_cuidador/', views.registrar_datos_cuidador, name='registro_datos_cuidador'),
    path('editar_datos_cuidador/', views.editar_datos_cuidador, name='editar_datos_cuidador'),
    path('solicitudes-cercanas/<int:cuidador_id>/', views.solicitudes_cercanas, name='solicitudes-cercanas'),
    path('solicitud/<int:solicitud_id>/', views.ver_solicitud, name='detalle_solicitud'),
    path('solicitud-aceptada/<int:solicitud_id>/', views.ver_solicitud_aceptada, name='detalle_solicitud_aceptada'),
    path('solicitudes-aceptadas/', views.ver_solicitudes_aceptadas, name='ver_solicitudes_aceptadas'),
    path('ver_solicitud/<int:solicitud_id>/', views.ver_solicitud_cliente, name='detalle_solicitud_cliente'),
    path('solicitud/editar/<int:solicitud_id>/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitud/eliminar/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('logout/', views.logout_view, name='logout'),
     path('listar_datos_propietario/', views.listar_datos_propietario, name='listar_datos_propietario'),
    path('registro_datos_propietario/', views.registrar_datos_propietario, name='registro_datos_propietario'),
    path('editar_datos_propietario/', views.editar_datos_propietario, name='editar_datos_propietario'),
    path('customer/', views.customer, name='customer'),  # Esta es la URL de la vista 'customer'
    path('inicio/',views.inicio, name='inicio'),
    path('listar-mascotas/', views.listar_mascotas, name='listar_mascotas'),
    path('agregar-mascota/', views.agregar_mascota, name='agregar_mascota'),
    path('editar-mascota/<int:pk>/', views.editar_mascota, name='editar_mascota'),
    path('eliminar-mascota/<int:pk>/', views.eliminar_mascota,name="eliminar_mascota"),
    path('cuidados/',views.cuidados,name='cuidados'),
    path('publicar-alojamiento/', views.publicar_alojamiento, name='publicar_alojamiento'),
    path('publicar-paseo/', views.publicar_paseo, name='publicar_paseo'),
    path('publicar-guarderia/', views.publicar_guarderia, name='publicar_guarderia'),
    path('publicar-peluqueria/', views.publicar_peluqueria, name='publicar_peluqueria'),
    path('eliminar-solicitud/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('solicitud/<int:solicitud_id>/aceptar/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('solicitud/<int:solicitud_id>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('contactar-cuidador/<int:cuidador_id>/', views.contactar_cuidador, name='contactar_cuidador'),
    path('mis-solicitudes/', views.listar_solicitudes_de_cuidado, name='listar_solicitudes_de_cuidado'),


    #URL DE API
    path('api/registro/', api_views.registro_api, name='api_registro'),

]
