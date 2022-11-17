from django.urls import path

from . import views

urlpatterns = [
    path('convs', views.convs, name='convs'),
    path('conv/<int:conv_id>', views.conv, name='conv'),
]