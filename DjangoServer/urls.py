from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news', views.news, name='news'),
    path('dream', views.dream, name='dream'),
    path('reload', views.reload, name='reload'),
    # Client API
    path('updateclient', views.updateClient, name='updateClient'),
    path('clientstatus', views.clientStatus, name='clientStatus'),
    path('removeclient', views.removeClient, name='removeClient'),
    path('dreamclient', views.dreamClient, name='dreamClient'),
]
