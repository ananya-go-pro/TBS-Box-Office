from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.helloworld,name='TBS'),
    path('home/',views.loginPage, name='home'),
    path('events/',include('events.urls')),
    path('logout/',views.logoutPage,name='logout'),
    path('details/<str:pk>/',views.details,name='details'),
    path('reports/',views.report,name="Greport"),
    path('adminlinks/',views.adminlinks, name='adminlinks'), 
    path('deleted/',views.deleted_data, name='deleted'),
]