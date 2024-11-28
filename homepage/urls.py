from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.helloworld,name='TBS'),
    path('home/',views.loginPage, name='home'),
    path('logout/',views.logoutPage,name='logout'),
    path('details/<str:pk>/',views.details,name='details'),
    path('reports/',views.report,name="Greport"),
    path('adminlinks/',views.adminlinks, name='adminlinks'), 
    path('deleted/',views.deleted_data, name='deleted'),
    path('events/',include('events.urls')),
] #There is no signup page as users can only be added in by admins.
#TODO once we get the csv database and know what it looks like, make a page to import users (create all data by self.)
