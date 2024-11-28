import datetime
from django.forms import DateTimeField
from django.shortcuts import render, redirect
from django.contrib import messages #this is what we import to get flash messages.
from django.contrib.auth.models import User
from .models import linkage,events,General,Family
from django.contrib.auth import authenticate,login,logout #imported for the user login
from django.contrib.auth.decorators import login_required,user_passes_test #this is used to restrict pages that need login or a certain login.
from csv import*
from django.utils import timezone
from events.views import encrypt,decrypt,secret_code_suadna,secret_code_55A555

#TODO push to new branch and merge branches later.
#TODO: server time to IST later
#TODO: email stuff!

class Small_trivial_functions():
    class Login():
        def input_usn_and_check_and_authenticate(request):
            username=request.POST.get('USN')
            password=request.POST.get('PWD')
            USN_exists=True

            try:
                user=User.objects.get(username=username) #try to get user
            except:#if user (USN) does not exist:
                USN_exists=Small_trivial_functions.Login.check_USN_and_create_emergency_users(username,password,request)
            
            user = authenticate(request,username=username,password=password)
            
            return(USN_exists,user)

        def check_USN_and_create_emergency_users(username,password,request):#else, if user is emergency user, execute a secret code that creates the users (uses own encyrption algorithm to be illegible to outsiders.)
            if username=="suadna":#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
                Small_trivial_functions.Login.check_and_create_suadna(username,password,request)
            elif username=="55A555":
                Small_trivial_functions.Login.check_and_create_55A555(username,password,request)
            else: #if usn isnt either emergency user.
                messages.error(request,'USN does not exist.')
                return(False)

        def check_and_create_suadna(username,password,request):
            encrypted_password,encrypted_create_user_code=secret_code_suadna()
            if encrypt(password,username) == encrypted_password: #if username and password are right
                exec(decrypt(encrypted_create_user_code,str(encrypted_password)))
            else:
                messages.error(request,'USN and password dont match.')
        
        def check_and_create_55A555(username,password,request):
            encrypted_password,encrypted_create_user_code,encrypted_user_create_family_code=secret_code_55A555()
            if encrypt(password,username)==encrypted_password:
                exec(decrypt(encrypted_create_user_code,str(encrypted_password)))
                exec(decrypt(encrypted_user_create_family_code,str(encrypted_password)))
            else:
                messages.error(request,'USN and password dont match.')

    def General_data_record(data_object):
        General_object_instance, created = General.objects.get_or_create(pk=1) #in case General_object_instance exists, get the first object. else, create it.
        exec(f"General_object_instance.{data_object}+=1") #just keeping track of the data.
        General_object_instance.save()

    class Details():
        def get_linkage_instance(pk): #this only works if the usn doesnt have a hyphen in it and the rest of the code is exactly as is.
            return(linkage.objects.get(user=User.objects.get(username=pk.split('-',1)[0]),event=events.objects.get(event=pk.split('-',1)[-1])))
        
        def get_details(linkage_instance): #this only works if the usn doesnt have a hyphen in it and the rest of the code is exactly as is.
            return({"USN":linkage_instance.user.username,"seats":linkage_instance.seats,"group":f"{linkage_instance.grp.group}","family":f"{linkage_instance.fami.Parent1}-{linkage_instance.fami.Parent2}-{linkage_instance.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"whenbooked":str(linkage_instance.whenbooked.strftime("%d/%m/%Y, %H:%M:%S")),"whenmade":str(linkage_instance.created.strftime("%d/%m/%Y, %H:%M:%S")),"details":linkage_instance.details,'emailsent':str(linkage_instance.emailsent.strftime("%d/%m/%Y, %H:%M:%S")),'event':linkage_instance.event})

def helloworld(request):
    return(render(request,'firstpage.html'))

def loginPage(request):
    if request.user.is_authenticated: 
        return(redirect('events'))

    if request.method=="POST":
        USN_exists,user=Small_trivial_functions.Login.input_usn_and_check_and_authenticate(request)
        
        if user:
            login(request,user)
            return(redirect('events'))
        elif USN_exists:
            messages.error(request,"Username and password don't match.")

    return(render(request,'hi.html'))

@login_required(login_url='home')
def logoutPage(request):
    Small_trivial_functions.General_data_record("logouts")
    logout(request) 
    return(redirect('home'))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them access this page.
def details(request,pk): #Admin comes here after scanning QR code.
    linkage_instance=Small_trivial_functions.Details.get_linkage_instance(pk)
    context=Small_trivial_functions.Details.get_details(linkage_instance)

    #TODO: check if this if is needed as seats need to be booked to generate a QR code right? 
    # what about if cancelled seats? think and see.
    if linkage_instance.seats==None: #if no seats booked, change whenbooked to none. (default would be when created.)
        context['whenbooked']=None
    linkage_instance.scanned=datetime.datetime.now()
    linkage_instance.save()

    Small_trivial_functions.General_data_record("QRscanned")

    event_instance=linkage_instance.event
    event_instance.scanned+=1
    event_instance.save()

    return(render(request,'details.html',context))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def report(request):
    General_object_instance, created = General.objects.get_or_create(pk=1)
    context={'logins':General_object_instance.logins,'logouts':General_object_instance.logouts,'emailsent':General_object_instance.emailsent,'QRscanned':General_object_instance.QRscanned,'Seatsbooked':General_object_instance.SeatsBooked,'Seatscancelled':General_object_instance.Seatscancelled,'whenupdated':General_object_instance.whenupdated}
    context['nosiblings']=sum([len([i for i in j.siblingsbooked.strip('\' ,"').split(',') if i not in '\' ,"']) for j in events.objects.all() if j.siblingsbooked])
    context['nowaiting']=sum([len([i for i in j.notifymail.split(',') if i not in ' ,']) for j in events.objects.all() if j.notifymail])
    return(render(request,'Grep.html',context))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def adminlinks(request):
    return(render(request,'linktree.html')) 

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def deleted_data(request):
    f=open('deleted_data.csv','r')
    r=reader(f)
    context={'deleted':[i for i in r]}
    f.close()
    return(render(request,'delete.html',context))