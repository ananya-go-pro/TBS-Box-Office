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
import ezgmail

@login_required(login_url='home') #just in case.
def home(request):
    context={'reports':False}
    if request.user.is_superuser:
        myevents=events.objects.all()
        context["reports"]=True
    else:
        GI, created = General.objects.get_or_create(pk=1)
        GI.logins+=1
        GI.save()
        myevents=[i.event for i in request.user.linkage_set.all()]#here I get only the events that belong to the user that has currently logged in
        if request.user.username=="55A555" and myevents==[]:#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
            try:
                event=events.objects.get(event="Test event")
                linkage_obj = linkage.objects.create(user=request.user,event=event,fami=Family.objects.get(user=request.user),seats="",maxseats=2,details="")              
                myevents=[event]
            except:
                event = events.objects.create(event="Test event",Date="2023-11-25 10:30:00.363473",Desc="Test event for demonstration and testing of features.",img="https://cdn4.iconfinder.com/data/icons/proglyphs-signs-and-symbols/512/Theatre-1024.png",red="default",blocked="A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11,A12,A13,A14,A15,A16,A17,B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,B11,B12,B13,B14,B15,B16,B17,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,",notifymail="",siblingsbooked="",entered=0,scanned=0,cancels=0,updatedon=timezone.now())
                linkage_obj = linkage.objects.create(user=request.user,event=event[0],fami=Family.objects.get(user=request.user),seats="",maxseats=2,details="")              
                myevents=[event]
    context['Events']=myevents
    return(render(request,'hi2.html',context))

@login_required(login_url='home') #just in case.
def hallplan(request,pk):
    context={'pk':pk}
    if request.user.is_superuser:
        return(redirect(f'/events/seatdetails/{pk}/'))
    else:
        try:
            event=(request.user.linkage_set.get(event__event=pk)).event #event__event is accessing that event(foriegn key)s event(attribute(name))
        except:
            return(redirect('home'))
        event.entered=event.entered+1
        event.save()
        context['allbooked']=(len(event.blocked.split(','))-1==476) #-1 is due to last comma being extra. This is so that we can see if all seats are taken.
        curlinkage=linkage.objects.get(user=request.user,event=event)
        if curlinkage.seats:#if already booked, send to ticket.
            return(redirect(f"/events/ticket/{pk}"))
        #Checking if the user has siblings that have booked in the same event.
        fam=Family.objects.get(user=request.user)
        sib=linkage.objects.filter(fami__Parent1=fam.Parent1,fami__Parent2=fam.Parent2,fami__Guardians=fam.Guardians,event=event)
        maxseats=curlinkage.maxseats
        for i in sib:
            if i.seats is not None:
                if curlinkage.event.siblingsbooked and f"{curlinkage.user.username}:{i.user.username}" not in curlinkage.event.siblingsbooked.split(','):
                    curlinkage.event.siblingsbooked+=f"{curlinkage.user.username}:{i.user.username},"
                    curlinkage.event.save()
                    return(render(request,'siblings.html',{'i':i}))
                else:
                    return(render(request,'siblings.html',{'i':i}))
            if event not in [i.event for i in request.user.linkage_set.all()]: #just in case
                return(redirect('home'))
        if request.method == "POST":
                    seats = request.POST.get('seats')  # Get selected seat IDs from POST data
                    seats=seats.strip('"')+','
                    event=(request.user.linkage_set.get(event__event=pk)).event#refreshing, to check real time, if anyone has booked that justt before this person booked.
                    if seats in event.blocked:#If somehow the seats have actually gotten booked just before the person clicked book, then reload the page.
                        return(redirect(f"/events/{event.red}"))
                    curlinkage.seats=seats
                    curlinkage.save()
                    taken=event.blocked
                    if taken == None:
                        taken=seats
                    else:
                        taken+=seats
                    event.blocked=taken
                    event.save()
                    GI, created = General.objects.get_or_create(pk=1)
                    GI.SeatsBooked+=1
                    GI.save()
                    return(redirect(f"/events/ticket/{pk}"))
        #see if you can make this more efficient.
        d={"maxseats":maxseats,"A":[],"B":[],"C":[],"D":[],"E":[],"F":[],"G":[],"H":[],"I":[],"J":[],"K":[],"L":[],"M":[],"N":[],"O":[],"AA":[],"BB":[],"CC":[],"DD":[],"EE":[],"FF":[]}
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
        ezgmail.send(recipients, subject=subject, body=message)
        GI, created = General.objects.get_or_create(pk=1)
        GI.emailsent+=1
        GI.save()
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
    ezgmail.send(recipients, subject=subject, body=message)
    GI, created = General.objects.get_or_create(pk=1)
    GI.emailsent+=1
    GI.save()
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
        return(redirect('home'))
    event.blocked=event.blocked.replace(curlinkage.seats,'')#removing those seats from events blocked seats.
    curlinkage.seats=None#removing seats from curlinkage.
    curlinkage.emailsent=None
    ezgmail.send(request.user.email, subject=f"Cancellation of your seats for {event} on {event.Date.strftime('%d/%m/%Y, %H:%M:%S')}", body=f"Your seats for {event} have been cancelled.\nPlease contact the school for further details.")
    curlinkage.save()
    event.cancels=event.cancels+1
    event.save()
    GI, created = General.objects.get_or_create(pk=1)
    GI.Seatscancelled+=1
    GI.save()
    
    if event.notifymail:
        for i in [j for j in event.notifymail.split(',') if j not in ' ,']:#now we send emails to all those who have been asked to be notified.
            ezgmail.send(i, subject=f"Availability of seats for {event}.", body=f"This is to notify you that a seat may be available for {event} as someone has cancelled their seats.\n\n If you do not wish to be notified about this further, please sign in and click this link: 127.0.0.1:8000/events/cancelnotify/{urllib.parse.quote(pk)}")
    return(redirect('home'))#can change this if wanted.

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
        deets.append({"USN":link.user.username,"seats":link.seats,"family":f"{link.fami.Parent1}-{link.fami.Parent2}-{link.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"whenbooked":str(link.whenbooked.strftime("%d/%m/%Y, %H:%M:%S")),"whenmade":str(link.created.strftime("%d/%m/%Y, %H:%M:%S")),"details":link.details,'emailsent':str(link.emailsent.strftime("%d/%m/%Y, %H:%M:%S")),'scan':scnd})
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

def wowstring():#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    return([140, 19, 151, 32, 11, 15, 11, 17, -16, 18, 10, 98, 151, 45, 82, 108, 62, 108, 92, 95, 96, 105, 74, 116, 88, 117, 81, 126, 78, 63, 71, 57, 102, 37],[116, 14, 159, 107, 15, -4, -12, 13, -4, 4, 3, 94, 139, 35, 73, 128, 76, 131, 85, 100, 87, 120, 78, 17, 66, 59, 80, 24, 71, 96, 75, 126, 83, 103, 65, 105, 76, 52, 66, 119, 80, 96, 83, 116, 80, 111, 74, 107, 79, 109, 78, 133, 62, 40, 85, 104, 62, 111, 84, 91, 74, 126, 68, 102, 73, 96, 87, 112, 71, 124, 86, 121, 64, 129, 61, 99, 80, 119, 65, 108, 81, 106, 70, 127, 78, 121, 95, 38, 71, 130, 72, 109, 83, 109, 71, 124, 71, 124, 67, 111, 83, 103, 73, 113, 67, 78, 78, 38, 69, 122, 72, 115, 89, 112, 82, 109, 73, 106, 68, 101, 81, 45, 78, 71, 93, 120, 76, 107, 72, 91, 81, 121, 58, 121, 67, 75, 85, 39, 90, 115, 66, 104, 72, 105, 67, 94, 76, 104, 90, 108, 68, 116, 73, 121, 75, 113, 74, 121, 77, 111, 78, 110, 74, 114, 80, 84, 64, 111, 82, 124, 66, 93, 81, 99, 84, 99, 83, 56, 78, 112, 73, 108, 80, 97, 74, 42, 62, 67, 87, 120, 94, 103, 52, 131, 79, 115, 63, 125, 60, 113, 74, 123, 81, 110, 78, 67, 83, 27, 70, 87, 71, 107, 63, 109, 70, 108, 84, 112, 78, 124, 66, 116, 64, 59, 79, 51, 80, 53, 80, 46, 62, 98, 83, 96, 82, 123, 74, 102, 69, 106, 78, 119, 67, 121, 79, 107, 86, 131, 55, 95, 80, 106, 86, 62, 64, 105, 89, 120, 59, 118, 73, 101, 71, 125, 58, 115, 72, 109, 82, 121, 76, 43, 92, 93, 64, 106, 81, 123, 81, 42, 68, 69, 72, 52, 65, 110, 72, 125, 69, 90, 72, 107, 95, 104, 70, 117, 80, 112, 86, 104, 81, 124, 74, 62, 73, 97, 71, 111, 75, 132, 77, 121, 92, 43, 62, 105, 82, 126, 62, 91, 73, 112, 85, 128, 73, 113, 81, 108, 88, 115, 70, 63, 50, 77, 87, 108, 69, 116, 88, 101, 72, 61, 67, 100, 84, 134, 68, 95, 81, 119, 67, 115, 70, 119, 75, 119, 85, 104, 85, 105, 87, 115, 72, 100, 83, 127, 69, 71, 68, 107, 73, 120, 75, 124, 88, 114, 72, 50, 97, 57])

def wowbro():#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    return([129, 2, 153, 35, 12, 17, 8, -4, -4, 9, 17, 75, 142, 53, 86, 55, 73, 61, 83, 88, 81, 76, 77, 89, 73, 96, 67, 54, 95, 41, 110, 46],[122, 9, 155, 133, 10, 10, -3, -1, 7, 9, 1, 99, 152, 44, 79, 135, 79, 113, 83, 118, 79, 125, 81, 48, 72, 107, 87, 119, 82, 117, 84, 124, 79, 110, 88, 134, 79, 106, 79, 118, 79, 102, 84, 111, 85, 38, 77, 76, 71, 41, 80, 93, 81, 123, 78, 104, 84, 125, 79, 59, 75, 129, 81, 104, 79, 112, 83, 110, 81, 110, 89, 117, 81, 127, 77, 49, 80, 112, 82, 125, 74, 111, 80, 102, 79, 134, 78, 119, 79, 103, 75, 127, 75, 124, 82, 111, 85, 134, 83, 55, 83, 123, 69, 120, 82, 102, 79, 127, 82, 123, 77, 112, 78, 118, 73, 102, 83, 74, 78, 50, 75, 61, 69, 61, 77, 70, 87, 54, 82, 64, 80, 66, 74, 58, 76, 55, 84, 116, 86, 118, 83, 104, 87, 116, 78, 113, 77, 76, 82, 51, 86, 136, 83, 123, 76, 104, 82, 109, 81, 118, 79, 104, 88, 124, 75, 127, 83, 125, 80, 124, 78, 104, 77, 107, 78, 114, 80, 74, 78, 110, 84, 107, 73, 98, 76, 112, 74, 122, 83, 60, 81, 105, 74, 123, 80, 115, 86, 53, 75, 53, 80, 127, 86, 101, 71, 125, 80, 131, 86, 130, 86, 122, 83, 123, 80, 106, 79, 70, 82, 44, 84, 70, 76, 59, 76, 87, 81, 78, 86, 97, 79, 96, 83, 68, 71, 61, 87, 51, 80, 57, 75, 118, 78, 102, 79, 114, 84, 103, 81, 100, 73, 124, 83, 118, 82, 106, 90, 119, 74, 108, 85, 104, 78, 70, 74, 128, 75, 116, 68, 124, 81, 117, 75, 134, 81, 115, 79, 121, 80, 102, 84, 55, 84, 111, 81, 126, 80, 132, 78, 56, 83, 42, 84, 51, 79, 114, 77, 134, 80, 106, 82, 112, 86, 107, 78, 125, 83, 100, 77, 125, 75, 112, 82, 69, 74, 100, 87, 130, 83, 133, 79, 110, 85, 46, 75, 113, 82, 120, 85, 98, 87, 121, 72, 130, 76, 108, 71, 104, 78, 113, 86, 71, 81, 73, 79, 106, 80, 120, 72, 127, 84, 120, 80, 61, 82, 118, 78, 109, 71, 102, 84, 128, 78, 126, 82, 116, 77, 109, 83, 127, 82, 119, 80, 130, 79, 105, 83, 127, 79, 84, 86, 85, 75, 118, 84, 116, 83, 122, 80, 110, 86, 43, 116, 51],[131, 10, 157, 191, 0, 2, -3, -4, 0, 11, 2, 95, 161, 49, 79, 86, 76, 100, 76, 121, 83, 109, 82, 119, 81, 129, 77, 64, 81, 123, 76, 107, 82, 108, 85, 110, 78, 100, 84, 124, 77, 125, 81, 60, 84, 111, 87, 119, 80, 106, 77, 111, 88, 129, 79, 113, 85, 49, 71, 133, 74, 135, 85, 111, 80, 136, 87, 56, 78, 127, 82, 119, 84, 112, 82, 119, 81, 56, 79, 95, 76, 107, 79, 121, 76, 112, 77, 119, 76, 131, 73, 49, 78, 77, 82, 47, 80, 99, 75, 101, 76, 109, 82, 118, 82, 109, 79, 110, 82, 130, 79, 64, 91, 48, 76, 85, 76, 106, 76, 128, 82, 110, 79, 112, 75, 125, 78, 56, 80, 71, 89, 54, 69, 94, 80, 111, 84, 114, 85, 114, 85, 123, 79, 107, 79, 53, 73, 49, 79, 79, 86, 129, 78, 105, 78, 122, 78, 108, 79, 111, 89, 104, 82, 125, 70, 126, 79, 71, 79, 59, 78, 126, 87, 112, 79, 36, 89, 116, 71, 117, 85, 104, 85, 36, 72, 111, 75, 105, 73, 122, 76, 112, 72, 124, 82, 131, 82, 57, 79, 53, 104, 54])

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
            ezgmail.send(i, subject=f"Availability of seats for {event}.", body=f"This is to notify you that a seat may be available for {event} as someone has cancelled their seats.\n\n If you do not wish to be notified about this further, please sign in and click this link: 127.0.0.1:8000/events/cancelnotify/{urllib.parse.quote(pk)}")
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
