from django.db import models as m
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver 
from csv import writer #for the deleted_data.csv file.
import urllib.parse

#TODO: Havent adressed deleting user-event linkages if the user is removed from the group that connected them (Tried in Usercheclinkages but have not done it.) (Rarely a problem but those are famous last words so try fixing it.)

#If migrate throws errors, delete and recreate the sqlite3 file, delete all files 
#from migrations except init files 
#(including pycache) then makemigrations and migrate again. this will remove all saved 
#data. so you will have to createsuperusers and then make all the stuff in the admin page. 
#or login as backup secret users

class General(m.Model): #keeps track of data (how many logins etc.)
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
    Date=m.DateTimeField()
    Desc=m.CharField(max_length=500,null=True)
    img=m.CharField(max_length=500,null=True)#image link to be rendered.
    red=m.CharField(max_length=100,default='default')#path to redirect on clicking (Usually the hall plan/.(default) but if an event demands a specific redirect, then that.)
    blocked=m.CharField(max_length=10000,null=True,default='A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11,A12,A13,A14,A15,A16,A17,B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,B11,B12,B13,B14,B15,B16,B17,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,')
    #blocking first three rows by default (cause we were isntructed to.)
    notifymail=m.CharField(max_length=1000000,default="",null=True,blank=True)#contains email_ids as email1,email2,... for those who asked to be notified when a seat opens up for this event.
    siblingsbooked=m.CharField(max_length=1000000,default="",null=True,blank=True)#contains the usns of those that couldnt book because their siblings had booked for the same event.
    entered=m.BigIntegerField(default=0) #number of clicks of event (asked as it may be used for event popularity later.)
    scanned=m.BigIntegerField(default=0) #number of people scanned and entered the hall.
    cancels=m.BigIntegerField(default=0) #number of people who booked and later cancelled their seats.
    updatedon=m.DateTimeField(auto_now=True) #last time any interaction was done with event (change in database)

    def __str__(self):
        return self.event #event name
    
    def save(self, *args, **kwargs): #when saving, if red=default, save red=book/event name
        if self.red=="default":
            self.red = f"book/{urllib.parse.quote(self.event)}/" #urlib.parse is just making the name into a url like format, (ex: spaces and all arent allowed in urls and are hence replaced by hyphens)
        super().save(*args, **kwargs)

    class Meta:
        unique_together=[['event']]#no repetition of same event names i think. TODO: check


class GroupEventLink(m.Model): #With this, we are making a group-event so that we can automate the user-event linkages for all users of that group to that event.
    group = m.ForeignKey('auth.Group', on_delete=m.CASCADE)
    event = m.ForeignKey(events, on_delete=m.CASCADE)

    def __str__(self):
        return f"{self.event}-{self.group}" 

    class Meta:
        unique_together=[['event','group']] #no repetetion.


@receiver(post_save, sender=GroupEventLink)#calls this function whenever a GroupEventLink is created.
def create_linkages_for_group(sender, instance, created, **kwargs):
    if created:
        for user in instance.group.user_set.all():#makes a event-user linkage for all users in that group to that event.
            if not linkage.objects.filter(event=instance.event,user=user).exists(): #if the user is aldready linked, do nothing.
                linkage.objects.create(event=instance.event, user=user,fami=Family.objects.get(user=user),grp=instance)#else, make the linkage

@receiver(pre_delete, sender=GroupEventLink)#just before a group event link gets deleted, we save the report of it in deleted_data.csv file and then delete all linkages related exclusively to that group-event linkage.
def deleteold(sender, instance, **kwargs): #this may cause problems where something was supposed to be deleted but the server stopped running while it was saving this data before deleting it.
    
    #TODO: IF ANY OVERLAPPING LINKAGES ARE THERE IN MULTIPLE GRP-EVENT-LINKS AND YOU SELECT ALL AND DELETE TOGETHER, THE OVERLAPPED ONES DONT GET DELETED. SINCE THEY GET DELETED TOGETHER, BOTH EXCLUDES THOSE LINKAGES ASSUMING THEY ARE IN THE OTHER GRP-EVENT LINKAGE.
    #      IT WORKS JUST FINE IF YOU DELETE THEM ONE BY ONE.
    #      IF YOU DELETE THE EVENT ITSELF, THE OVERLAPPING LINKAGES WILL BE DELETED, HOWEVER THOSE LINKAGES WONT APPEAR IN THE deleted_data.csv THIS IS BECAUSE THE SAME PROBLEM HAPPENS BUT THE EVENT ITSELF DELETES THE LINKAGE DUE TO THE CASCADE IN THE FORIEGN KEY.
    #      HOWEVER, SINCE OVERLAPPING OF LINKAGES IS A RARE CASE AND I COULDNT FIND A QUICK AND SIMPLE FIX, I AM LEAVING IT WITH THESE TWO PROBLEMS.


    event = instance.event 
    group = instance.group
    other_grps_linked=GroupEventLink.objects.filter(event=event).exclude(pk=instance.pk) #other groups-event linkages with the same event
    linkages_to_delete = linkage.objects.filter(event=event, user__groups=group) #all linkages in that event-group link
    f=open('deleted_data.csv','a')
    w=writer(f,lineterminator="\r") #if this still leaves blanks bw lines, use newline=''
    deltd,scnd=0,0 #counts
    deets=[]
    dates={}
    for i in linkages_to_delete: #storing in deleted_data.csv and deleting the linkage for all linkages that belong to this group-event linkage exclusively.
        for j in other_grps_linked: #exclusively from this group event link => delete, else, leave.
            if i.user in j.group.user_set.all():
                break 
        else: #if doesnt break => if exclusively in this grp-event link => to be deleted
            deltd+=1
            if i.seats: #if he had booked seats #TODO: check what this does and if it is nessecary.
                if i.scanned: #if he had entered
                    scnd+=1
                    wait=str(i.scanned.strftime("%d/%m/%Y, %H:%M:%S"))
                else:
                    wait='' #to keep it as string and avoid not defined error #TODO: check if nessecary

                if dates.get(str(i.whenbooked.date())):#data stuff for reports
                    dates[str(i.whenbooked.date())]+=1 
                elif not dates.get(str(i.whenbooked.date())):
                    dates[str(i.whenbooked.date())]=1 

                deets.append({"USN":i.user.username,"seats":i.seats,"family":f"{i.fami.Parent1}-{i.fami.Parent2}-{i.fami.Guardians}".replace("None","").replace("--", "-").strip("-"),"whenbooked":str(i.whenbooked.strftime("%d/%m/%Y, %H:%M:%S")),"whenmade":str(i.created.strftime("%d/%m/%Y, %H:%M:%S")),"details":i.details,'emailsent':str(i.emailsent.strftime("%d/%m/%Y, %H:%M:%S")),'scan':wait})
            i.delete()

    #putting in csv #TODO: check if you want it in a diff format, clean up this bit.

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

@receiver(post_save, sender=Family)#when a user is newly created (and added to groups), check if any event linkages to be made for him. (on saving of family, runs this.)
def Userchecklinkages(sender, instance, created, **kwargs): 
    for grp in instance.user.groups.all():
        grpevents=grp.groupeventlink_set.all()
        for i in grpevents:
            if not linkage.objects.filter(event=i.event, user=instance.user).exists(): #if user aldready linked to event, leave
                linkage.objects.create(event=i.event, user=instance.user,fami=instance,grp=i)#else, link user to event using this group.

    #TODO: tries to delete the user-event linkages when the user is removed from the group, didnt work for some reason, have left it be as it is rarely a problem.
    '''
    for i in instance.user.linkage_set.all():#checking if the linkage is still valid. If we remove the user's groups, the linkage authorised through that group should be deleted.
        grpevents=GroupEventLink.objects.filter(event=i.event,group__user=instance.user)
        if grpevents==[]:#if this linkage(for i in all linkages of that user) belongs to some existing group of that user, do nothing
            i.delete()  #if it does not belong to any of that users groups, delete it.'''#FIX THIS. ITS RARELY A PROBLEM THO.


class linkage(m.Model): #this is where we define the unique attributes to each user-event linkage.
    event = m.ForeignKey(events, on_delete=m.CASCADE)
    user=m.ForeignKey(User,on_delete=m.CASCADE)
    grp=m.ForeignKey(GroupEventLink,on_delete=m.DO_NOTHING,null=True,blank=True)
    fami=m.ForeignKey(Family,on_delete=m.SET_NULL,null=True)
    seats=m.CharField(max_length=10,blank=True,null=True)#will be filled automatically when booked
    maxseats=m.IntegerField(default=2)
    whenbooked=m.DateTimeField(auto_now=True)
    created=m.DateTimeField(auto_now_add=True)
    #TODO: delete this ticket thing?
    #ticket=m.ImageField(blank=True,null=True) #(can delete, no problem) if needed to save ticket as an image, generally a bad idea, leads to server load. If needed to save the tickets/QRs somehow, save it as a byte64 encrypted string instead.
    details=m.CharField(max_length=500,blank=True,null=True)#ticketdetails must be filled automatically when booked.
    emailsent=m.DateTimeField(blank=True,null=True)
    scanned=m.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f"{self.user.username}-{self.event}"
    
    class Meta:
        unique_together=[['event','user']] #unsure how important this is, but leaving it be. #TODO: check if its useful to add seats and such in this too, although not needed as there it is automated and there is no direct human input except buttons.
        #this means that we can put/ link a user in an event only once.


#currently not the most efficient system, nor is it bug free, when dealing with large number of users and huge amount of data, it is prone to errors. In case of such errors, django's admin side is pretty intuitive and one can easily go and manually add what is missing for certain users or delete and create new ones if it is malfunctioning. 
#The best practise is to keep the data fresh, avoid duplication and keep it minimal and avoid adding users in strange ways randomly in between.
# After every year, the students must be purged from the database and new ones added with their new groups. 

#my advice to best use the system is to create/import users with their groups and family details every year.
#Then create events an group event links when needed, once the event is over, take the data and stats if needed and delete the group event links one by one, then delete the event
#since when deleting the event directly, if there are users who are not exclusive to one group connected to that event, it might not delete or get recorded.
#Hence causing more dead users to be in the system which could lead to problems and hassles in managing.
#If there are users added after creation of grp-event links and added to those grps, the system should handle it, but it is always a good practise to check the users when you add a 
# group-event link and further to check specific user linkages when those users are added later/seperately.
#Further, at the end of every academic year, the users must all be removed (except superusers and staff) and new users must be imported/added with their new respective groups.
#If there is a recurring/repeating event every year, DO NOT use the same event and run with the same old data trying to cancel and rebook or anything of the sort. instead
#Delete the old grp-event linkages and the old event and create a new event and add the grp-event linkages. Use the system in a minimal way to keep it as simple as possible.
#In case all the users of a system get deleted including the Superusers, there are two ways to get back into the system to operate it and add users as a superuser.
#The tedious first method is to go to the server, stop it and run the djang-admin create superuser command. 
# But there is another way which does not need nearly as much knowledge/effort and one can simply log in via the backup/emergency users of which one is a superuser and the other is a test user. 
# Please contact the developer at surajacharya2005@gmail.com to know more in case this happens. 
