from django.db import models as m
from datetime import *
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver 
from csv import* #for the deleted_data.csv file.
import urllib.parse

'''If migrate throws errors, delete and recreate the sqlite3 file, delete all files from migrations except 001 files and init files 
(including pycache) then makemigrations and migrate again. this will remove all saved data. so you will have to createsuperusers
and then make all the stuff in the admin page.'''

class General(m.Model):
    logins=m.BigIntegerField(default=0)
    logouts=m.BigIntegerField(default=0)
    emailsent=m.BigIntegerField(default=0)
    QRscanned=m.BigIntegerField(default=0)
    SeatsBooked=m.BigIntegerField(default=0)
    Seatscancelled=m.BigIntegerField(default=0)
    whenupdated=m.DateTimeField(auto_now=True)#technically, useless ish


class Family(m.Model): # FYI: It has all the attributes of User such as .is_authenticated etc... since it has inherited from User via onetoone
    user = m.OneToOneField(User, on_delete=m.CASCADE,related_name='me')# this is just to make a onetoone connection between a user and this.
    Parent1 = m.CharField(max_length=200)
    Parent2 = m.CharField(max_length=200, blank=True)
    Guardians = m.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}-{self.Parent1}-{self.Parent2}-{self.Guardians}".replace('None','').replace("--", "-").strip("-")  

class events(m.Model):
    event=m.CharField(max_length=200)
    # attendees=m.ManyToManyField(User, through='linkage') #this linkage class that we call allows
    # #the many to many linkage while also allowing each link/pair to have its own unique attributes
    Date=m.DateTimeField()
    Desc=m.CharField(max_length=500,null=True)
    img=m.CharField(max_length=500,null=True)#image link to be rendered.
    red=m.CharField(max_length=100,default='default')#path to redirect on clicking (Usually the hall plan.(default) 
    #If aldready booked, then to ticket page. But in an event like the carnival, directly to ticket page.)
    blocked=m.CharField(max_length=10000,null=True,default='A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11,A12,A13,A14,A15,A16,A17,B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,B11,B12,B13,B14,B15,B16,B17,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,')
    #blocking first three rows by default.pyt
    notifymail=m.CharField(max_length=1000000,default="",null=True,blank=True)#contains emails as email1,email2,... like seats booked.
    siblingsbooked=m.CharField(max_length=1000000,default="",null=True,blank=True)#contains the usns of those that couldnt book because their siblings had booked.
    entered=m.BigIntegerField(default=0)
    scanned=m.BigIntegerField(default=0)
    cancels=m.BigIntegerField(default=0)
    updatedon=m.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event
    
    def save(self, *args, **kwargs):
        if self.red=="default":
            self.red = f"book/{urllib.parse.quote(self.event)}/"
        super().save(*args, **kwargs)

    class Meta:
        unique_together=[['event']]


class GroupEventLink(m.Model): #With this, we are linking a group to an event so that we dont have to make a linkage for each user manually.
    #we only have to link the event to the group and then django should handle the induvidual attributes to be unique for each user.
    group = m.ForeignKey('auth.Group', on_delete=m.CASCADE)
    event = m.ForeignKey(events, on_delete=m.CASCADE)
    def __str__(self):
        return f"{self.event}-{self.group}"
    class Meta:
        unique_together=[['event','group']]


@receiver(post_save, sender=GroupEventLink)#calls the function whenever a GroupEventLink is created.
def create_linkages_for_group(sender, instance, created, **kwargs):
    if created:
        for user in instance.group.user_set.all():#makes a linkage for all users in that group to that event.
            if not linkage.objects.filter(event=instance.event,user=user).exists(): #if the user is aldready linked, do nothing.
                linkage.objects.create(event=instance.event, user=user,fami=Family.objects.get(user=user))#else, make the linkage

@receiver(pre_delete, sender=GroupEventLink)#whenever a group event link gets deleted, we save the report of it in deleted_data.csv file and then delete all linkages related exclusively to that group-event linkage.
def deleteold(sender, instance, **kwargs):
    event = instance.event
    group = instance.group
    other_grps_linked=GroupEventLink.objects.filter(event=event).exclude(pk=instance.pk)
    linkages_to_delete = linkage.objects.filter(event=event, user__groups=group)
    f=open('deleted_data.csv','a')
    w=writer(f,lineterminator="\r") #if this still leaves blanks bw lines, use newline=''
    deltd,scnd=0,0
    deets=[]
    dates={}
    for i in linkages_to_delete: #storing in deleted_data.csv and deleting the linkage for all linkages that belong to this group-event linkage exclusively.
        for j in other_grps_linked:
            if i.user in j.group.user_set.all():
                #IMP!!!
                #IF ANY OVERLAPPING LINKAGES ARE THERE IN MULTIPLE GRP-EVENT-LINKS AND YOU SELECT ALL AND DELETE, THE OVERLAPPED ONES DONT GET DELETED.
                #SINCE THEY GET DELETED TOGETHER, BOTH EXCLUDES THOSE LINKAGES ASSUMING THEY ARE IN THE OTHER GRP-EVENT LINKAGE.
                #IT WORKS JUST FINE IF YOU DELETE THEM ONE BY ONE.
                #IF YOU DELETE THE EVENT ITSELF, THE OVERLAPPING LINKAGES WILL BE DELETED, HOWEVER THOSE LINKAGES WONT APPEAR IN THE deleted_data.csv
                #THIS IS BECAUSE THE SAME PROBLEM HAPPENS BUT THE EVENT ITSELF DELETES THE LINKAGE DUE TO THE CASCADE IN THE FORIEGN KEY.
                #HOWEVER, SINCE OVERLAPPING OF LINKAGES IS A RARE CASE AND I COULDNT FIND A QUICK AND SIMPLE FIX, I AM LEAVING IT WITH THESE TWO PROBLEMS.
                #IMP!!!
                break
        else:
            deltd+=1
            if i.seats:
                if i.scanned:
                    scnd+=1
                    wait=str(i.scanned.strftime("%d/%m/%Y, %H:%M:%S"))
                else:
                    wait=''
                if dates.get(str(i.whenbooked.date())):
                    dates[str(i.whenbooked.date())]+=1
                elif not dates.get(str(i.whenbooked.date())):
                    dates[str(i.whenbooked.date())]=1
                deets.append({"USN":i.user.username,"seats":i.seats,"family":f"{i.fami.Parent1}-{i.fami.Parent2}-{i.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"whenbooked":str(i.whenbooked.strftime("%d/%m/%Y, %H:%M:%S")),"whenmade":str(i.created.strftime("%d/%m/%Y, %H:%M:%S")),"details":i.details,'emailsent':str(i.emailsent.strftime("%d/%m/%Y, %H:%M:%S")),'scan':wait})
            i.delete()
    #putting in csv
    #main stuff:
    w.writerows([[],[],[f"General details of deleted {event}-{group} group-event-link only"],["Group: ",group],["Event: ",event],["Date and time of deletion: ",timezone.now().strftime("%d/%m/%Y, %H:%M:%S")],["Number of linkages in event: ",len(linkages_to_delete)],["Number of linkages deleted: ",deltd],["Number of linkages booked: ",sum(dates.values())],[f"Number of linkages scanned: ",scnd],["Number of seats blocked: ",len(event.blocked.split(','))],["Number of seats booked: ","Yet to do"],[]])
    f.flush()#just in case
    #booking log:
    w.writerow(["Booking log: "])
    w.writerow(["Date:","No of Bookings:"])
    w.writerows(dates.items())
    w.writerow([])
    f.flush()#just in case
    #Overall:
    w.writerow(["Overall: "])
    if deets:
        w.writerow(deets[0])
        w.writerow([])
        for i in deets:
            w.writerow([i[j] for j in i])
    w.writerows([[],[]])
    f.flush()#just in case
    f.close()

@receiver(post_save, sender=Family)
def Userchecklinkages(sender, instance, created, **kwargs):#to check if theres any new linkages to be made if a user is newely added (after the groupeventlink is added) or freshly added to that group.
    for grp in instance.user.groups.all():
        grpevents=grp.groupeventlink_set.all()
        for i in grpevents:
            if not linkage.objects.filter(event=i.event, user=instance.user).exists(): #if user aldready linked to event, leave
                linkage.objects.create(event=i.event, user=instance.user,fami=instance,grp=i)#else, link user to event using this.
    '''
    for i in instance.user.linkage_set.all():#checking if the linkage is still valid. If we remove the user's groups, the linkage authorised through that group should be deleted.
        grpevents=GroupEventLink.objects.filter(event=i.event,group__user=instance.user)
        if grpevents==[]:#if this linkage(for i in all linkages of that user) belongs to some existing group of that user, do nothing
            i.delete()  #if it does not belong to any of that users groups, delete it.'''#FIX THIS. ITS RARELY A PROBLEM THO.

class linkage(m.Model): #this is where we define the unique attributes to each link/pair.
    event = m.ForeignKey(events, on_delete=m.CASCADE)
    user=m.ForeignKey(User,on_delete=m.CASCADE)
    fami=m.ForeignKey(Family,on_delete=m.SET_NULL,null=True)
    seats=m.CharField(max_length=10,blank=True,null=True)#will be filled automatically when booked
    maxseats=m.IntegerField(default=2)
    whenbooked=m.DateTimeField(auto_now=True)
    created=m.DateTimeField(auto_now_add=True)
    #ticket=m.ImageField(blank=True,null=True)
    details=m.CharField(max_length=500,blank=True,null=True)#ticketdetails must be filled automatically when booked.
    emailsent=m.DateTimeField(blank=True,null=True)
    scanned=m.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f"{self.user.username}-{self.event}"
    
    class Meta:#YET TO FINISH, ask group and finish.
        unique_together=[['event','user']]# a list of fields that should be associated together / unique together.
        #this means that we can put/ link a user in an event only once.
        #try adding this for seats etc also...

    #can acces with get, blah blah.
    #to add via code, can get that particular event and then say event.user.add(<user>,through_defaults={'seats':'12,32'})
    #event.save()
    #if user.events.all() doesnt work to get the data, try user.events_set.all()
