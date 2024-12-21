from datetime import *
from django.utils import timezone
from io import BytesIO
import json
from django.http import HttpResponse
from django.shortcuts import render,redirect
from homepage.models import linkage, Family, events, General
from django.contrib.auth.decorators import login_required,user_passes_test
import urllib.parse
import qrcode
import base64
#from django.core.mail import send_mail
#import ezgmail (TODO: email stuff figure out.) IMP

current_domain='127.0.0.1:8000/'

#TODO: havent tested allbooked

class Small_trivial_functions():
    def General_data_record(data_object):
        General_object_instance, created = General.objects.get_or_create(pk=1) #in case General_object_instance exists, get the first object. else, create it.
        exec(f"General_object_instance.{data_object}+=1") #just keeping track of the data.
        General_object_instance.save()

    class Test_event_for_emergency_user(): 
        def create_linkage(request):
            event=events.objects.get(event="Test event")
            linkage_obj = linkage.objects.create(user=request.user,event=event,fami=Family.objects.get(user=request.user),seats="",maxseats=2,details="")
            return([event])

        def create_event():
            event = events.objects.create(event="Test event",Date="2023-11-25 10:30:00.363473",Desc="Test event for demonstration and testing of features.",img="https://cdn4.iconfinder.com/data/icons/proglyphs-signs-and-symbols/512/Theatre-1024.png",red="default",blocked="A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11,A12,A13,A14,A15,A16,A17,B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,B11,B12,B13,B14,B15,B16,B17,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,",notifymail="",siblingsbooked="",entered=0,scanned=0,cancels=0,updatedon=timezone.now())

        def check_event_exists_and_create(request):
            #For any information on this and the emergency users, contact the dev at surajacharya2005@gmail.com
            try: 
                event=events.objects.get(event="Test event")
                my_event=Small_trivial_functions.Test_event_for_emergency_user.create_linkage(request)
            except: 
                Small_trivial_functions.Test_event_for_emergency_user.create_event()
                my_event=Small_trivial_functions.Test_event_for_emergency_user.create_linkage(request)
            return(my_event)

    class Hallplan():
        def get_event_object(request,event_name):
            return(request.user.linkage_set.get(event__event=event_name)).event #checking foriegn keys of all linkages of that user to get that event.

        def check_if_event_full(event): #returns a true/false
            return(len(event.blocked.split(','))-1==476) #-1 is due to last comma being extra. This is so that we can see if all seats are taken.

        def update_event_siblingsbooked(curlinkage,event,sibling): #update event records adding names of users who couldnt book because their siblings have.
            if event.siblingsbooked and f"{curlinkage.user.username}:{sibling.user.username}" not in event.siblingsbooked.split(','):
                event.siblingsbooked+=f"{curlinkage.user.username}:{sibling.user.username},"
                event.save()

        def check_for_siblings_bookings(request,curlinkage): #have been told to let a pair of parents book only once for an event.
            fam=Family.objects.get(user=request.user)
            sibling_who_booked=False
            event=curlinkage.event

            siblings_in_same_event=[i for i in linkage.objects.filter(fami__Parent1=fam.Parent1,fami__Parent2=fam.Parent2,fami__Guardians=fam.Guardians,event=event) if i.user != request.user]
            for sibling in siblings_in_same_event:
                if sibling.seats:
                    sibling_who_booked=sibling
                    Small_trivial_functions.Hallplan.update_event_siblingsbooked(curlinkage,event,sibling)
            
            return (sibling_who_booked)

        def get_latest_event_instance(request,event_name):
            return((request.user.linkage_set.get(event__event=event_name)).event)

        def check_if_seats_still_available(event,selected_seats):
            #reloading page if selected seats not empty in latest version of events.
            if selected_seats in event.blocked:
                return(redirect(f"/events/{event.red}"))

        def update_event_blocked(event,selected_seats):
            all_taken_seats=event.blocked #includes booked and reserved seats.
            if all_taken_seats == None:
                all_taken_seats=selected_seats
            else:
                all_taken_seats+=selected_seats
            event.blocked=all_taken_seats
            event.save()
            
        def initialize_hallplan_details(curlinkage):
            #keeping default empty values for all so that it can easily be accesed in js without having to worry wether the key exists.
            return({"maxseats_user_can_book":curlinkage.maxseats,"A":[],"B":[],"C":[],"D":[],"E":[],"F":[],"G":[],"H":[],"I":[],"J":[],"K":[],"L":[],"M":[],"N":[],"O":[],"AA":[],"BB":[],"CC":[],"DD":[],"EE":[],"FF":[]})
       

class Medium_funcs():
    class Hallplan():

        def precautionary_check_redirect_ticket_and_siblings(request,curlinkage,event_name):
            #redirect to ticket page if aldready booked
            if curlinkage.seats: 
                return(redirect(f"/events/ticket/{event_name}"))

            #redirect to siblings page if sibling has booked (have been asked to let a pair of parents book only once.)
            sibling_who_booked=Small_trivial_functions.Hallplan.check_for_siblings_bookings(request,curlinkage)
            if sibling_who_booked:
                return(render(request,'siblings.html',{'i':sibling_who_booked}))

        def handle_post_data(request,curlinkage,event_name):
            selected_seats = request.POST.get('selected-seats').strip('"')+','
            event=Small_trivial_functions.Hallplan.get_latest_event_instance(request,event_name)
                    
            Small_trivial_functions.Hallplan.check_if_seats_still_available(event,selected_seats) #precuationary

            curlinkage.seats=selected_seats
            curlinkage.save()
                    
            Small_trivial_functions.Hallplan.update_event_blocked(event,selected_seats)
                    
            Small_trivial_functions.General_data_record('SeatsBooked')

            return(redirect(f"/events/ticket/{event_name}"))

        def get_json_hallplan_details_for_js(event,curlinkage):
            
            hallplan_details=Small_trivial_functions.Hallplan.initialize_hallplan_details(curlinkage)         
            all_taken_seats=event.blocked.split(',')[:-1] #includes booked and reserved seats
            #TODO: clean this
            for i in all_taken_seats: 
                for j in range(len(i)): #iterating through the seat ID to put them into hallplan_details
                    if i[j].isdigit():
                        try:
                            temp=hallplan_details[i[:j]]
                            temp.append(int(i[j:]))
                            hallplan_details[i[:j]]=temp
                        except:
                            #this shouldnt happen but just in case the admin has entered some bad data in the blocked.
                            hallplan_details[i[:j]]=[int(i[j:])]
                        break

            
            hallplan_details=json.dumps(hallplan_details).replace("'", '"') #replaces the '' in the dict to "" so that we can pass it to the js (through the html.)
            return(hallplan_details)
            

@login_required(login_url='home') #must be logged in to access events.
def eventspage(request):
    context={'admin':False} #default
    if request.user.is_superuser: 
        myevents=events.objects.all()#passes all events to HTML cause admin can access all.
        context["admin"]=True #this is passed to a check in the HTML as the UI is different for admins
    else:
        Small_trivial_functions.General_data_record('logins')

        myevents=[i.event for i in request.user.linkage_set.all()]
        if request.user.username=="55A555" and myevents==[]:
            myevents=Small_trivial_functions.Test_event_for_emergency_user.check_event_exists_and_create(request)

    context['Events']=myevents
    return(render(request,'hi2.html',context))


@login_required(login_url='home') #precautionary.
def hallplan(request,pk): 
    context={}
    event_name=pk

    if request.user.is_superuser: #admin can see seatdetails page when they click the event.
        return(redirect(f'/events/seatdetails/{event_name}/')) 
    else:

        try:
            event=Small_trivial_functions.Hallplan.get_event_object(request,event_name)
        except: #precautionary
            return(redirect('home')) #TODO: add an error message here (using django flash messages)

        curlinkage=linkage.objects.get(user=request.user,event=event)

        event.entered=event.entered+1 #keeping this before all redirects so even those are counted.
        event.save()
        
        Medium_funcs.Hallplan.precautionary_check_redirect_ticket_and_siblings(request,curlinkage,event_name)
        #TODO: test this, i havent after latest change.

        if request.method == "POST":
                    Medium_funcs.Hallplan.handle_post_data(request,curlinkage,event_name)
        
        hallplan_details=Medium_funcs.Hallplan.get_json_hallplan_details_for_js(curlinkage,event)

        context['blocked']=hallplan_details #to pass to javascript and render all seats accordingly.
        context['event']=event
        context['allbooked']=Small_trivial_functions.Hallplan.check_if_event_full(event)#if all seats taken, render notify button.
        context['notify_path']=event_name #sending event_name to html to have event specific redirects (here for notify).
        return(render(request,'audi.html',context))
    
#TODO: I WAS HERE
@login_required(login_url='home')
def ticket(request,pk):
    try:
        event=(request.user.linkage_set.get(event__event=pk)).event #event__event is accessing that event(foriegn key)s event(attribute(name))
    except:
        return(redirect('home'))
    curlinkage=linkage.objects.get(user=request.user,event=event)
    if event not in [i.event for i in request.user.linkage_set.all()]:
        return(redirect('home'))
    if curlinkage.seats==None:#if not booked, send home.
        return(redirect('home'))
    if event.notifymail and request.user.email in event.notifymail.split(','): #if the user has asked to notify and has now gotten a seat/seats, remove his name from notify.
        temp=event.notifymail
        event.notifymail=temp.replace(request.user.email,'')
        event.save()
    url="127.0.0.1:8000/"+urllib.parse.quote(f'details/{curlinkage}')#HERE, THE 127.0.0.1:8000 WILL HAVE TO BE CHANGED TO THE DOMAIN.
    img=qrcode.make(url) #this is a PILImage.
    buffered = BytesIO()#this will be the image as a string. need the bytes as that way, i can encode the pilimage into bytes
    #and then decode that into a string.
    img.save(buffered) #saving image into buffered. (as bytes prolly.)
    image_str = base64.b64encode(buffered.getvalue()).decode() #making the image into a string that can be sent and rendered in ticket.
    context={'Event':event,'EventDeets':event.Date,'desc':event.Desc,'seats':curlinkage.seats,'bookedwhen':curlinkage.whenbooked.strftime("%d/%m/%Y, %H:%M:%S"),'QR':image_str,'pk':pk,'email':request.user.email}
    if curlinkage.emailsent==None:#if email has not been sent, send an email.
        #Sending the email from suadnastorage.
        subject=f"Your ticket for {event} on {event.Date.strftime('%d/%m/%Y, %H:%M:%S')}"
        message=f"Ticket: \n\n Link: 127.0.0.1:8000/events/ticket/{urllib.parse.quote(pk)}/ \n\n Event: {event} \n\n Date and time: {event.Date.strftime('%d/%m/%Y, %H:%M:%S')} \n\n Description: {event.Desc} \n\n Your seats: {curlinkage.seats} \n\n For QR code, please visit the link. \n\n Booked on: {curlinkage.whenbooked.strftime('%d/%m/%Y, %H:%M:%S')} \n\n For any queries, please contact the school."
        #fromwhom='suadnastorage@gmail.com'
        recipients=request.user.email
        #ezgmail.send(recipients, subject=subject, body=message) #TODO make ezgmail work
        General_object_instance, created = General.objects.get_or_create(pk=1)
        General_object_instance.emailsent+=1
        General_object_instance.save()
        #send_mail(subject, message, fromwhom, recipients,fail_silently=False)
        curlinkage.emailsent=timezone.now()
        curlinkage.save()
    return(render(request,'ticket.html',context))


@login_required(login_url='home')
def resend(request,pk):
    try:
        event=(request.user.linkage_set.get(event__event=pk)).event #event__event is accessing that event(foriegn key)s event(attribute(name))
    except:
        return(redirect('home'))
    curlinkage=linkage.objects.get(user=request.user,event=event)
    if event not in [i.event for i in request.user.linkage_set.all()]:
        return(redirect('home'))
    if curlinkage.seats==None:#if not booked, send home.
        return(redirect('home'))
    #Sending the email from suadnastorage.
    subject=f"Your ticket for {event} on {event.Date.strftime('%d/%m/%Y, %H:%M:%S')}"
    message=f"Ticket: \n\n Link: 127.0.0.1:8000/events/ticket/{urllib.parse.quote(pk)}/ \n\n Event: {event} \n\n Date and time: {event.Date.strftime('%d/%m/%Y, %H:%M:%S')} \n\n Description: {event.Desc} \n\n Your seats: {curlinkage.seats} \n\n For QR code, please visit the link. \n\n Booked on: {curlinkage.whenbooked.strftime('%d/%m/%Y, %H:%M:%S')} \n\n For any queries, please contact the school."
    #fromwhom='suadnastorage@gmail.com'
    recipients=request.user.email
    #ezgmail.send(recipients, subject=subject, body=message) #TODO make ezgmail work
    General_object_instance, created = General.objects.get_or_create(pk=1)
    General_object_instance.emailsent+=1
    General_object_instance.save()
    #send_mail(subject, message, fromwhom, recipients,fail_silently=False)
    curlinkage.emailsent=timezone.now()
    curlinkage.save()
    return(redirect(f'/events/ticket/{pk}/'))

@login_required(login_url='home')
def cancel(request,pk):
    try:
        event=(request.user.linkage_set.get(event__event=pk)).event #event__event is accessing that event(foriegn key)s event(attribute(name))
    except:
        return(redirect('home'))
    curlinkage=linkage.objects.get(user=request.user,event=event)
    if event not in [i.event for i in request.user.linkage_set.all()]:
        return(redirect('home'))
    if curlinkage.seats==None:#if not booked, send home.
        return(redirect('home'))
    if curlinkage.seats not in event.blocked:#If its not there, we dont have to cancel anything. (all these are just fallbacks, JICs)
        return(redirect('home')) #TODO: DISPLAY ERROR MESSAGES HERE AND ALL 
        #TODO: FIX THIS, WHEN ITS NOT IN EVENT.Blocked cancel it in curlinkage atleast!
    event.blocked=event.blocked.replace(curlinkage.seats,'')#removing those seats from events blocked seats.
    curlinkage.seats=None#removing seats from curlinkage.
    curlinkage.emailsent=None
    #ezgmail.send(request.user.email, subject=f"Cancellation of your seats for {event} on {event.Date.strftime('%d/%m/%Y, %H:%M:%S')}", body=f"Your seats for {event} have been cancelled.\nPlease contact the school for further details.")
    #TODO make ezgmail work
    curlinkage.save()
    event.cancels=event.cancels+1
    event.save()
    General_object_instance, created = General.objects.get_or_create(pk=1)
    General_object_instance.Seatscancelled+=1
    General_object_instance.save()
    
    if event.notifymail:
        for i in [j for j in event.notifymail.split(',') if j not in ' ,']:#now we send emails to all those who have been asked to be notified.
            #ezgmail.send(i, subject=f"Availability of seats for {event}.", body=f"This is to notify you that a seat may be available for {event} as someone has cancelled their seats.\n\n If you do not wish to be notified about this further, please sign in and click this link: 127.0.0.1:8000/events/cancelnotify/{urllib.parse.quote(pk)}")
            #TODO make ezgmail work.
            pass #TODO remove.
    return(redirect('home'))#can change this if wanted.

#TODO: REPLACE WITH CLEANED ENCRYPT AND TEST
def encrypt(contents,that): #For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    import random as rn
    key=''
    for i in that:
        for j in range(ord(i)*2):
            rn.seed(j)
            t=str(rn.randint(0,1000))
            key+=t
    rn.seed(ord(key[0])+int(key[-1]))
    t=rn.randint(0,len(key)//2)
    key=key[t::]
    if len(key)>2000:
        key=key[0:2000]
    import pickle
    out=[]
    ke,tempo=0,0
    a=int(key[1])
    for i in contents:
        out.append(ord(i))
    for i in range(a):
        for j in range(len(out)):
            try:
                ke=int(key[tempo])
            except IndexError:
                tempo=0
                ke=int(key[tempo])
            tempo+=1
            if i%2==0:
                out[j]=out[j]+ke
            else:
                out[j]=out[j]-ke
    d=open('store.dat','wb')
    pickle.dump(out,d)
    d.close()
    key=key[::-1]
    d=open('store.dat','r',encoding='iso-8859-15')
    con=d.read()
    out=[]
    ke,tempo=0,0
    a=int(key[1])
    for i in con:
        out.append(ord(i))
    for i in range(a):
        for j in range(len(out)):
            try:
                ke=int(key[tempo])
            except IndexError:
                tempo=0
                ke=int(key[tempo])
            tempo+=1
            if i%2==0:
                out[j]=out[j]+ke
            else:
                out[j]=out[j]-ke
    d.close()
    key=key[::-1]
    import os
    os.remove('store.dat')
    return(out)

#TODO: REPLACE WITH CLEANED VERSION FROM ENCRYPT AND TEST
def decrypt(out,that):#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    import random as rn
    key=''
    for i in that:
        for j in range(ord(i)*2):
            rn.seed(j)
            t=str(rn.randint(0,1000))
            key+=t
    rn.seed(ord(key[0])+int(key[-1]))
    t=rn.randint(0,len(key)//2)
    key=key[t::]
    if len(key)>2000:
        key=key[0:2000]
    import pickle
    ke,tempo=0,0
    key=key[::-1]
    a=int(key[1])
    for i in range(a):
        for j in range(len(out)):
            try:
                ke=int(key[tempo])
            except IndexError:
                tempo=0
                ke=int(key[tempo])
            tempo+=1
            if i%2==0:
                out[j]=out[j]-ke
            else:
                out[j]=out[j]+ke
    data=''
    for i in out:
        data+=str(chr(i))
    key=key[::-1]
    d=open('store.dat','w',encoding='iso-8859-15')
    d.write(data)
    d.close()
    d=open('store.dat','rb')
    out=pickle.load(d)
    d.close()
    ke,tempo=0,0
    a=int(key[1])
    for i in range(a):
        for j in range(len(out)):
            try:
                ke=int(key[tempo])
            except IndexError:
                tempo=0
                ke=int(key[tempo])
            tempo+=1
            if i%2==0:
                out[j]=out[j]-ke
            else:
                out[j]=out[j]+ke
    content=''
    for i in out:
        content+=str(chr(i))
    import os
    os.remove('store.dat')
    return(content)

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def seatdetails(request,pk):
    event=(events.objects.get(event=pk))
    deets={}
    d={"A":[],"B":[],"C":[],"D":[],"E":[],"F":[],"G":[],"H":[],"I":[],"J":[],"K":[],"L":[],"M":[],"N":[],"O":[],"AA":[],"BB":[],"CC":[],"DD":[],"EE":[],"FF":[],"SA":[],"SB":[],"SC":[],"SD":[],"SE":[],"SF":[],"SG":[],"SH":[],"SI":[],"SJ":[],"SK":[],"SL":[],"SM":[],"SN":[],"SO":[],"SAA":[],"SBB":[],"SCC":[],"SDD":[],"SEE":[],"SFF":[],"RA":[],"RB":[],"RC":[],"RD":[],"RE":[],"RF":[],"RG":[],"RH":[],"RI":[],"RJ":[],"RK":[],"RL":[],"RM":[],"RN":[],"RO":[],"RAA":[],"RBB":[],"RCC":[],"RDD":[],"REE":[],"RFF":[]}
    #keeping default empty values for all so that it can easily be accesed in js without having to worry wether the key exists.
    l=event.blocked.split(',')
    l.pop()    
    for i in l: #traversing the list of booked seats
        link= [k for k in linkage.objects.filter(event=event) if k.seats!=None and i in k.seats.split(',')] #contains only the linkage which booked that seat.
        if link==[]: #reserved seats
            for j in range(len(i)):
                #rendering seats as usual
                if i[j].isdigit():
                    try:
                        temp=d[f"R{i[:j]}"]
                        temp.append(int(i[j:]))
                        d[f"R{i[:j]}"]=temp
                    except:
                        #this shouldnt happen but just in case the admin has entered some bad data in the blocked.
                        d[f"R{i[:j]}"]=[int(i[j:])]
                    break
            deets[i]=None #if this seat is blocked but not through a linkage, then set it as none
        elif link!=[]: #Non reserved seats
            link=link[0] #else, set deets[that seat] as the linkage which was used to book it.
            deets[i]=json.dumps({"event":link.event.event,"USN":link.user.username,"family":f"{link.fami.Parent1}-{link.fami.Parent2}-{link.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"seats":link.seats,"whenbooked":str(link.whenbooked.strftime("%d/%m/%Y, %H:%M:%S")),"whenmade":str(link.created.strftime("%d/%m/%Y, %H:%M:%S")),"details":link.details,'emailsent':str(link.emailsent.strftime("%d/%m/%Y, %H:%M:%S")),'scannedon':str(link.scanned)}).replace("'", '"')
            if link.scanned!=None: #scanned seats
                for j in range(len(i)):
                    #rendering seats as usual
                    if i[j].isdigit():
                        try:
                            temp=d[f"S{i[:j]}"]
                            temp.append(int(i[j:]))
                            d[f"S{i[:j]}"]=temp
                        except:
                            #this shouldnt happen but just in case the admin has entered some bad data in the blocked.
                            d[f"S{i[:j]}"]=[int(i[j:])]
                        break  
            else: #Booked but not scanned seats  
                for j in range(len(i)):
                    #rendering seats as usual
                    if i[j].isdigit():
                        try:
                            temp=d[i[:j]]
                            temp.append(int(i[j:]))
                            d[i[:j]]=temp
                        except:
                            #this shouldnt happen but just in case the admin has entered some bad data in the blocked.
                            d[i[:j]]=[int(i[j:])]
                        break
    #deets now contains all the booked seats of that event: who booked them. Now, we take this to JS (through hidden form) then there, we call the deets[selectedseat] which is the linkage and then get all the data of the seat from there and display it.
    # d is just so that we can pass the same booked seats of that event in a nice form so aditi can go make the booked things.
    context={"deets":json.dumps(deets).replace("'", '"'),"blocked":json.dumps(d).replace("'", '"'),"event":event}#replaces the '' in the dict to "" so that we can pass it to the js (through the html.)
    return(render(request,'adminaudi.html',context))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def report(request,pk):
    event=(events.objects.get(event=pk))
    links=[k for k in linkage.objects.filter(event=event) if k.seats!=None]
    context={'whenupdated':event.updatedon.strftime("%d/%m/%Y, %H:%M:%S"),'scanned':event.scanned,'blocked':len(event.blocked.split(',')),'pplsbooked':len(links),'clicked':event.entered,'cancelled':event.cancels,"event":event.event,'nowaiting':0,'nosiblings':0}
    if event.siblingsbooked:
        context['nosiblings']=len([i for i in event.siblingsbooked.strip('\' ,"').split(',') if i not in '\' ,"'])
    if event.notifymail:
        context['notiymail']=len([i for i in event.notifymail.split(',') if i not in ' ,'])
    deets=[]
    dates={}
    for link in links:
        if dates.get(str(link.whenbooked.date())):
            dates[str(link.whenbooked.date())]+=1
        else:
            dates[str(link.whenbooked.date())]=1
        if link.scanned:
            scnd=str(link.scanned.strftime("%d/%m/%Y, %H:%M:%S"))
        else:
            scnd=''
        deets.append({"USN":link.user.username,"seats":link.seats,"grp":f"{link.grp}","family":f"{link.fami.Parent1}-{link.fami.Parent2}-{link.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"whenbooked":str(link.whenbooked.strftime("%d/%m/%Y, %H:%M:%S")),"whenmade":str(link.created.strftime("%d/%m/%Y, %H:%M:%S")),"details":link.details,'emailsent':str(link.emailsent.strftime("%d/%m/%Y, %H:%M:%S")),'scan':scnd})
    context['deets']=deets
    l=dates.items()
    dates=[]
    for i in l:
        temp=[]
        for j in i:
            temp.append(j)
        dates.append(temp)
    context['dates']=dates
    return(render(request, 'info.html',context))

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.    
def reserve(request,pk): #this was a last minute addition, literally about to have the meeting when i realised this feature could be nice. It is just a workaround, there is a much more efficient way of doin this where it is just in the hallplan() itself.
    context={'pk':pk} #Here, were just blocking the seats as an admin.
    event=(events.objects.get(event=pk))
    if request.method == "POST":
        seats = request.POST.get('seats')  # Get selected seat IDs from POST data
        seats=seats.strip('"')+','
        event=(events.objects.get(event=pk))#refreshing, to check real time, if anyone has booked that justt before this person booked.
        if seats in event.blocked:#If somehow the seats have actually gotten booked just before the person clicked book, then reload the page.
            return(redirect(f"/events/{event.red}"))
        taken=event.blocked
        if taken == None:
            taken=seats
        else:
            taken+=seats
        event.blocked=taken
        event.save()
        return(redirect('home'))
    #see if you can make this more efficient.
    d={"maxseats":69420,"A":[],"B":[],"C":[],"D":[],"E":[],"F":[],"G":[],"H":[],"I":[],"J":[],"K":[],"L":[],"M":[],"N":[],"O":[],"AA":[],"BB":[],"CC":[],"DD":[],"EE":[],"FF":[]}
    #keeping default empty values for all so that it can easily be accesed in js without having to worry wether the key exists.
    s=event.blocked
    l=s.split(',')
    l.pop()
    for i in l: 
        for j in range(len(i)):
            if i[j].isdigit():
                try:
                    temp=d[i[:j]]
                    temp.append(int(i[j:]))
                    d[i[:j]]=temp
                except:
                    #this shouldnt happen but just in case the admin has entered some bad data in the blocked.
                    d[i[:j]]=[int(i[j:])]
                break
    d=json.dumps(d).replace("'", '"') #replaces the '' in the dict to "" so that we can pass it to the js (through the html.)
    context['blocked']=d
    context['event']=event
    return(render(request,'audi.html',context))

@login_required(login_url='home') #this function is another last minute added feauture. If all seats are booked for that event,
def notify(request,pk): #it will send an email to whoever clicks notify my whenever someone cancels and the event gets free.
    #this function is only to add the email ID to notify (in event model). the sending of the emails will happen in cancel.
    context={}
    try:
        event=(request.user.linkage_set.get(event__event=pk)).event #event__event is accessing that event(foriegn key)s event(attribute(name))
    except:
        return(redirect('home'))
    #confirming that it is really full.
    context['allbooked']=(len(event.blocked.split(','))-1==476) #-1 is due to last comma being extra. This is so that we can see if all seats are taken.
    curlinkage=linkage.objects.get(user=request.user,event=event)
    #confirming that the criteria for inform is met. i.e They must not have aldready booked a ticket and they must not have siblings who have booked it.
    #there will be a check in ticket to remove any and all emails that have booked from inform.
    if curlinkage.seats:#if aldready booked, send to ticket.
            return(redirect(f"/events/ticket/{pk}"))
    #checking for siblings.
    fam=Family.objects.get(user=request.user)
    sib=linkage.objects.filter(fami__Parent1=fam.Parent1,fami__Parent2=fam.Parent2,fami__Guardians=fam.Guardians,event=event)
    for i in sib:
        if i.seats is not None:
            curlinkage.event.siblingsbooked+=f"{curlinkage.user.username}:{i.user.username},"
            curlinkage.event.save()
            return(render(request,'siblings.html',{'i':i}))  
        if event not in [i.event for i in request.user.linkage_set.all()]: #just in case
            return(redirect('home'))
    #checking if aldready asked for this.
    if event.notifymail and request.user.email not in event.notifymail.split(','):
        #adding to list.
        event.notifymail+=request.user.email+','
        event.save()
    context['email']=request.user.email
    return(render(request,'notify.html',context))
@login_required(login_url='home')
def cancelnotify(request,pk):
    context={}
    try:
        event=(request.user.linkage_set.get(event__event=pk)).event #event__event is accessing that event(foriegn key)s event(attribute(name))
    except:
        return(redirect('home'))
    if event.notifymail and request.user.email in event.notifymail.split(','): #if the user has asked to notify and has now gotten a seat/seats, remove his name from notify.
        temp=event.notifymail
        event.notifymail=temp.replace(f"{request.user.email},",'')
        event.save()
    return(redirect('home'))

def secret_code_suadna():#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    encrypted_password=[140, 19, 151, 32, 11, 15, 11, 17, -16, 18, 10, 98, 151, 45, 82, 108, 62, 108, 92, 95, 96, 105, 74, 116, 88, 117, 81, 126, 78, 63, 71, 57, 102, 37]
    encrypted_create_user_code=[116, 14, 159, 107, 15, -4, -12, 13, -4, 4, 3, 94, 139, 35, 73, 128, 76, 131, 85, 100, 87, 120, 78, 17, 66, 59, 80, 24, 71, 96, 75, 126, 83, 103, 65, 105, 76, 52, 66, 119, 80, 96, 83, 116, 80, 111, 74, 107, 79, 109, 78, 133, 62, 40, 85, 104, 62, 111, 84, 91, 74, 126, 68, 102, 73, 96, 87, 112, 71, 124, 86, 121, 64, 129, 61, 99, 80, 119, 65, 108, 81, 106, 70, 127, 78, 121, 95, 38, 71, 130, 72, 109, 83, 109, 71, 124, 71, 124, 67, 111, 83, 103, 73, 113, 67, 78, 78, 38, 69, 122, 72, 115, 89, 112, 82, 109, 73, 106, 68, 101, 81, 45, 78, 71, 93, 120, 76, 107, 72, 91, 81, 121, 58, 121, 67, 75, 85, 39, 90, 115, 66, 104, 72, 105, 67, 94, 76, 104, 90, 108, 68, 116, 73, 121, 75, 113, 74, 121, 77, 111, 78, 110, 74, 114, 80, 84, 64, 111, 82, 124, 66, 93, 81, 99, 84, 99, 83, 56, 78, 112, 73, 108, 80, 97, 74, 42, 62, 67, 87, 120, 94, 103, 52, 131, 79, 115, 63, 125, 60, 113, 74, 123, 81, 110, 78, 67, 83, 27, 70, 87, 71, 107, 63, 109, 70, 108, 84, 112, 78, 124, 66, 116, 64, 59, 79, 51, 80, 53, 80, 46, 62, 98, 83, 96, 82, 123, 74, 102, 69, 106, 78, 119, 67, 121, 79, 107, 86, 131, 55, 95, 80, 106, 86, 62, 64, 105, 89, 120, 59, 118, 73, 101, 71, 125, 58, 115, 72, 109, 82, 121, 76, 43, 92, 93, 64, 106, 81, 123, 81, 42, 68, 69, 72, 52, 65, 110, 72, 125, 69, 90, 72, 107, 95, 104, 70, 117, 80, 112, 86, 104, 81, 124, 74, 62, 73, 97, 71, 111, 75, 132, 77, 121, 92, 43, 62, 105, 82, 126, 62, 91, 73, 112, 85, 128, 73, 113, 81, 108, 88, 115, 70, 63, 50, 77, 87, 108, 69, 116, 88, 101, 72, 61, 67, 100, 84, 134, 68, 95, 81, 119, 67, 115, 70, 119, 75, 119, 85, 104, 85, 105, 87, 115, 72, 100, 83, 127, 69, 71, 68, 107, 73, 120, 75, 124, 88, 114, 72, 50, 97, 57]
    return(encrypted_password,encrypted_create_user_code)

def secret_code_55A555():#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    encrypted_password=[129, 2, 153, 35, 12, 17, 8, -4, -4, 9, 17, 75, 142, 53, 86, 55, 73, 61, 83, 88, 81, 76, 77, 89, 73, 96, 67, 54, 95, 41, 110, 46]
    encrypted_create_user_code=[127, 5, 157, 100, 8, 3, 8, -1, 8, 11, 3, 93, 158, 49, 70, 129, 83, 117, 76, 123, 78, 128, 79, 38, 79, 72, 83, 50, 80, 91, 75, 122, 70, 102, 79, 128, 81, 54, 84, 117, 81, 102, 82, 115, 78, 109, 82, 109, 83, 129, 75, 125, 82, 63, 81, 110, 83, 122, 81, 121, 75, 104, 83, 125, 70, 111, 81, 98, 74, 131, 86, 115, 83, 107, 90, 117, 83, 43, 82, 136, 74, 130, 72, 108, 72, 124, 80, 120, 89, 110, 78, 121, 77, 111, 85, 67, 76, 49, 77, 62, 83, 56, 79, 73, 84, 55, 82, 63, 81, 61, 79, 56, 80, 54, 74, 106, 78, 122, 77, 114, 83, 114, 78, 110, 73, 66, 83, 47, 88, 129, 85, 132, 77, 114, 70, 110, 78, 113, 85, 110, 83, 131, 80, 126, 74, 125, 69, 121, 80, 107, 75, 115, 79, 107, 75, 66, 81, 106, 87, 119, 85, 108, 82, 114, 78, 125, 79, 60, 77, 116, 88, 115, 82, 126, 87, 56, 76, 52, 81, 131, 73, 107, 77, 118, 84, 115, 74, 128, 80, 116, 88, 121, 81, 111, 86, 67, 74, 52, 78, 63, 76, 66, 89, 69, 70, 87, 82, 99, 86, 105, 87, 59, 79, 57, 71, 51, 78, 45, 82, 107, 78, 120, 84, 121, 85, 112, 75, 92, 77, 115, 77, 121, 89, 123, 79, 126, 79, 106, 81, 117, 86, 75, 77, 125, 75, 108, 82, 111, 75, 114, 83, 139, 82, 115, 80, 118, 78, 109, 80, 52, 80, 116, 74, 112, 75, 128, 77, 42, 79, 64, 81, 53, 84, 120, 78, 126, 78, 98, 87, 97, 80, 110, 87, 125, 80, 120, 77, 121, 72, 115, 75, 60, 85, 97, 74, 129, 81, 128, 83, 111, 85, 54, 88, 113, 76, 119, 83, 102, 78, 123, 79, 123, 79, 100, 76, 112, 78, 115, 84, 68, 84, 84, 79, 102, 77, 122, 83, 123, 78, 110, 81, 58, 76, 126, 84, 123, 83, 96, 78, 125, 81, 134, 75, 124, 77, 115, 83, 119, 78, 126, 86, 125, 81, 111, 73, 125, 78, 70, 70, 81, 79, 111, 78, 119, 78, 118, 90, 103, 78, 54, 105, 46]
    encrypted_user_create_family_code=[134, 14, 155, 214, 6, 7, 3, 0, 7, 6, 9, 99, 148, 48, 72, 110, 72, 98, 77, 128, 87, 123, 80, 114, 77, 130, 81, 107, 78, 128, 82, 110, 74, 108, 89, 74, 73, 76, 90, 111, 79, 110, 82, 115, 85, 107, 82, 123, 78, 64, 74, 120, 78, 111, 76, 119, 83, 104, 78, 119, 76, 132, 85, 122, 77, 57, 80, 111, 82, 118, 86, 107, 86, 110, 85, 126, 84, 107, 78, 51, 79, 129, 74, 124, 76, 115, 85, 135, 72, 76, 82, 126, 75, 122, 77, 112, 80, 126, 74, 50, 84, 85, 69, 101, 85, 115, 81, 116, 79, 121, 79, 130, 83, 62, 72, 68, 85, 44, 76, 97, 80, 97, 75, 112, 83, 113, 74, 108, 88, 108, 79, 126, 75, 58, 74, 57, 86, 88, 90, 99, 84, 133, 75, 114, 74, 116, 74, 136, 72, 58, 88, 77, 85, 43, 85, 85, 74, 103, 84, 108, 86, 117, 83, 120, 76, 115, 78, 54, 73, 63, 80, 77, 79, 127, 79, 110, 88, 116, 75, 108, 79, 109, 75, 104, 82, 121, 81, 122, 84, 75, 80, 53, 74, 119, 76, 104, 83, 46, 84, 125, 79, 128, 76, 105, 79, 47, 81, 121, 83, 109, 84, 115, 85, 101, 77, 137, 80, 126, 81, 41, 80, 57, 108, 51]
    return(encrypted_password,encrypted_create_user_code,encrypted_user_create_family_code)

@user_passes_test(lambda u: u.is_superuser,login_url='home') #if user is admin, let them see this page.
def cancelreserve(request,pk):
    context={'pk':pk} #Here, were just blocking the seats as an admin.
    event=(events.objects.get(event=pk))
    if request.method == "POST":
        seats = request.POST.get('seats')  # Get selected seat IDs from POST data
        seats=seats.strip('"')+','
        taken=event.blocked
        for i in seats.strip(' ,').split(','):
            taken=taken.replace(f'{i},','')#removing those seats from events blocked seats.
        event.blocked=taken
        event.save()
        return(redirect('home'))
    d={"RA":[],"RB":[],"RC":[],"RD":[],"RE":[],"RF":[],"RG":[],"RH":[],"RI":[],"RJ":[],"RK":[],"RL":[],"RM":[],"RN":[],"RO":[],"RAA":[],"RBB":[],"RCC":[],"RDD":[],"REE":[],"RFF":[]}
    #keeping default empty values for all so that it can easily be accesed in js without having to worry wether the key exists.
    l=event.blocked.split(',')
    l.pop()    
    for i in l: #traversing the list of booked seats
        link= [k for k in linkage.objects.filter(event=event) if k.seats!=None and i in k.seats.split(',')] #contains only the linkage which booked that seat.
        if link==[]: #reserved seats
            for j in range(len(i)):
                #rendering seats as usual
                if i[j].isdigit():
                    try:
                        temp=d[f"R{i[:j]}"]
                        temp.append(int(i[j:]))
                        d[f"R{i[:j]}"]=temp
                    except:
                        #this shouldnt happen but just in case the admin has entered some bad data in the blocked.
                        d[f"R{i[:j]}"]=[int(i[j:])]
                    break
    if event.notifymail:
        for i in [j for j in event.notifymail.split(',') if j not in ' ,']:#now we send emails to all those who have been asked to be notified.
            #ezgmail.send(i, subject=f"Availability of seats for {event}.", body=f"This is to notify you that a seat may be available for {event} as someone has cancelled their seats.\n\n If you do not wish to be notified about this further, please sign in and click this link: 127.0.0.1:8000/events/cancelnotify/{urllib.parse.quote(pk)}")
            #TODO make ezgmail work
            pass
    #deets now contains all the booked seats of that event: who booked them. Now, we take this to JS (through hidden form) then there, we call the deets[selectedseat] which is the linkage and then get all the data of the seat from there and display it.
    # d is just so that we can pass the same booked seats of that event in a nice form so aditi can go make the booked things.
    context={"blocked":json.dumps(d).replace("'", '"')}#replaces the '' in the dict to "" so that we can pass it to the js (through the html.)
    context['event']=event
    return(render(request,'cancelaudi.html',context))

#REMOVE WHENMADE AND ADD WHICH EMAIL IT HAS BEEN SENT TO IN ADMINAUDI.
#same way replace linkage made on in report

#Change api account so that it says tbsboxoffice.

# reserved, booked, taken (currently its just how many seats taken,
# i want to show how many of those are resered and how many booked), 
# not booked yet, how many booked but not entered yet. All must be added to reports
