from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login_view,name='login'),
    path('registro/',views.registro,name='registro'),
    path("registroAdmin/", views.registroAdmin, name="registroAdmin"),
    path('employee/', views.employee, name='employee'),
    path('listar_datos_cuidador/', views.listar_datos_cuidador, name='listar_datos_cuidador'),
    path('registro_datos_cuidador/', views.registrar_datos_cuidador, name='registro_datos_cuidador'),
    path('editar_datos_cuidador/', views.editar_datos_cuidador, name='editar_datos_cuidador'),
    path('solicitudes-cercanas/<int:cuidador_id>/', views.solicitudes_cercanas, name='solicitudes-cercanas'),
    path('solicitud/<int:solicitud_id>/', views.ver_solicitud, name='detalle_solicitud'),

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
    path('mis-solicitudes/', views.listar_solicitudes_de_cuidado, name='listar_solicitudes_de_cuidado'),
]
