from django.contrib import admin
from .models import events,linkage,Family,GroupEventLink,General
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(events)
admin.site.register(GroupEventLink)

class CustomUserAdmin(UserAdmin):
    """
    In the Django admin site, after editing a user's profile, this
    function redirects the admin to the Family page to view make changes
        obj (User): The user object being changed. Right now whichever
        user is saved, that object gets passed into the
        obj argument in this function
    HttpResponseRedirect: A redirect to /family/<id>/change with
    the user's ID as an argument.
    """
    def response_change(self, request, obj) -> HttpResponseRedirect: # if you get an error on this line remove the type annotations
            try: 
                if obj.me:#checking if users family has aldready been made
                    return HttpResponseRedirect(reverse("admin:homepage_family_change", args=[obj.me.id]))
            except:
                Family.objects.create(user=obj) # creates a family object with everything None except the onetoone
                return HttpResponseRedirect(reverse("admin:homepage_family_change", args=[obj.me.id]))
"""
I am unregistering the default Django User, and registering it again
in conjunction with the CustomUserAdmin class we just created.
All attributes of User will still be retained!
"""
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(General)
admin.site.register(Family)
admin.site.register(linkage)