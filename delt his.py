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

def wowstring():
    hehe=encrypt("coconut30","suadna")
    wowstring=encrypt('user = User.objects.create_superuser(username="suadna",email="suadnastorage@gmail.com",password="coconut30",date_joined=timezone.now(),is_active=True,is_staff=True,is_superuser=True)',str(hehe))
    return(hehe,wowstring) #no variables please

def wowbro():
    hehe=encrypt("25ENOV23","55A555")
    s="user,family_obj = User.objects.create_user(username='55A555',email='suadnastorage@gmail.com',password='25ENOV23',date_joined=timezone.now(),is_active=True,is_staff=False,is_superuser=False)"
    b="Family.objects.create(user=user,Parent1='Ranjeet',Parent2='Rajini',Guardians='of the galaxy')"
    wowstring=encrypt(s,str(hehe))
    return(hehe,wowstring,encrypt(b,str(hehe)))

a,b=wowstring()
c,d,e=wowbro()
print(a,'\n\n',b,'\n\n',c,'\n\n',d,'\n\n',e)

print(decrypt(d,str(c)))
print(decrypt(e,str(c)))
