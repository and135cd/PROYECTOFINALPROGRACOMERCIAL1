from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login_view, name='login_view'),
    path('registro',views.registro,name='registro'),
]