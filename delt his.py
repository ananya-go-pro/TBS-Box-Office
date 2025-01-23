#THIS IS NOT MEANT TO BE SEEN BY ANYONE, IF THIS IS SEEN BY ANYONE BUT surajacharya2005@gmail.com, DO ME A FAVOR AND LET ME KNOW PLEASE.
'''
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
    hehe=encrypt("coconut30","suadna") #contents=password,key=username
    wowstring=encrypt('user = User.objects.create_superuser(username="suadna",email="suadnastorage@gmail.com",password="coconut30",date_joined=timezone.now(),is_active=True,is_staff=True,is_superuser=True)',str(hehe))
    return(hehe,wowstring) #no variables please

def wowbro():
    hehe=encrypt("25ENOV23","55A555")
    s="user = User.objects.create_user(username='55A555',email='suadnastorage@gmail.com',password='25ENOV23',date_joined=timezone.now(),is_active=True,is_staff=False,is_superuser=False)"
    b="family_obj=Family.objects.create(user=user,Parent1='Ranjeet',Parent2='Rajini',Guardians='of the galaxy')"
    wowstring=encrypt(s,str(hehe))
    return(hehe,wowstring,encrypt(b,str(hehe)))


a,b=wowstring()
c,d,e=wowbro()
print(a,'\n\n',b,'\n\n',c,'\n\n',d,'\n\n',e)

print(decrypt(d,str(c)))
print(decrypt(e,str(c)))

'''

'''


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



def secret_code_suadna():#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    encrypted_password=[140, 19, 151, 32, 11, 15, 11, 17, -16, 18, 10, 98, 151, 45, 82, 108, 62, 108, 92, 95, 96, 105, 74, 116, 88, 117, 81, 126, 78, 63, 71, 57, 102, 37]
    encrypted_create_user_code=[116, 14, 159, 107, 15, -4, -12, 13, -4, 4, 3, 94, 139, 35, 73, 128, 76, 131, 85, 100, 87, 120, 78, 17, 66, 59, 80, 24, 71, 96, 75, 126, 83, 103, 65, 105, 76, 52, 66, 119, 80, 96, 83, 116, 80, 111, 74, 107, 79, 109, 78, 133, 62, 40, 85, 104, 62, 111, 84, 91, 74, 126, 68, 102, 73, 96, 87, 112, 71, 124, 86, 121, 64, 129, 61, 99, 80, 119, 65, 108, 81, 106, 70, 127, 78, 121, 95, 38, 71, 130, 72, 109, 83, 109, 71, 124, 71, 124, 67, 111, 83, 103, 73, 113, 67, 78, 78, 38, 69, 122, 72, 115, 89, 112, 82, 109, 73, 106, 68, 101, 81, 45, 78, 71, 93, 120, 76, 107, 72, 91, 81, 121, 58, 121, 67, 75, 85, 39, 90, 115, 66, 104, 72, 105, 67, 94, 76, 104, 90, 108, 68, 116, 73, 121, 75, 113, 74, 121, 77, 111, 78, 110, 74, 114, 80, 84, 64, 111, 82, 124, 66, 93, 81, 99, 84, 99, 83, 56, 78, 112, 73, 108, 80, 97, 74, 42, 62, 67, 87, 120, 94, 103, 52, 131, 79, 115, 63, 125, 60, 113, 74, 123, 81, 110, 78, 67, 83, 27, 70, 87, 71, 107, 63, 109, 70, 108, 84, 112, 78, 124, 66, 116, 64, 59, 79, 51, 80, 53, 80, 46, 62, 98, 83, 96, 82, 123, 74, 102, 69, 106, 78, 119, 67, 121, 79, 107, 86, 131, 55, 95, 80, 106, 86, 62, 64, 105, 89, 120, 59, 118, 73, 101, 71, 125, 58, 115, 72, 109, 82, 121, 76, 43, 92, 93, 64, 106, 81, 123, 81, 42, 68, 69, 72, 52, 65, 110, 72, 125, 69, 90, 72, 107, 95, 104, 70, 117, 80, 112, 86, 104, 81, 124, 74, 62, 73, 97, 71, 111, 75, 132, 77, 121, 92, 43, 62, 105, 82, 126, 62, 91, 73, 112, 85, 128, 73, 113, 81, 108, 88, 115, 70, 63, 50, 77, 87, 108, 69, 116, 88, 101, 72, 61, 67, 100, 84, 134, 68, 95, 81, 119, 67, 115, 70, 119, 75, 119, 85, 104, 85, 105, 87, 115, 72, 100, 83, 127, 69, 71, 68, 107, 73, 120, 75, 124, 88, 114, 72, 50, 97, 57]
    return(encrypted_password,encrypted_create_user_code)

def secret_code_55A555():#For any information on this, contact the dev @ suadnastorage@gmail.com (if no reply, can contact surajacharya2005@gmail.com)
    encrypted_password=[129, 2, 153, 35, 12, 17, 8, -4, -4, 9, 17, 75, 142, 53, 86, 55, 73, 61, 83, 88, 81, 76, 77, 89, 73, 96, 67, 54, 95, 41, 110, 46]
    encrypted_create_user_code=[127, 5, 157, 100, 8, 3, 8, -1, 8, 11, 3, 93, 158, 49, 70, 129, 83, 117, 76, 123, 78, 128, 79, 38, 79, 72, 83, 50, 80, 91, 75, 122, 70, 102, 79, 128, 81, 54, 84, 117, 81, 102, 82, 115, 78, 109, 82, 109, 83, 129, 75, 125, 82, 63, 81, 110, 83, 122, 81, 121, 75, 104, 83, 125, 70, 111, 81, 98, 74, 131, 86, 115, 83, 107, 90, 117, 83, 43, 82, 136, 74, 130, 72, 108, 72, 124, 80, 120, 89, 110, 78, 121, 77, 111, 85, 67, 76, 49, 77, 62, 83, 56, 79, 73, 84, 55, 82, 63, 81, 61, 79, 56, 80, 54, 74, 106, 78, 122, 77, 114, 83, 114, 78, 110, 73, 66, 83, 47, 88, 129, 85, 132, 77, 114, 70, 110, 78, 113, 85, 110, 83, 131, 80, 126, 74, 125, 69, 121, 80, 107, 75, 115, 79, 107, 75, 66, 81, 106, 87, 119, 85, 108, 82, 114, 78, 125, 79, 60, 77, 116, 88, 115, 82, 126, 87, 56, 76, 52, 81, 131, 73, 107, 77, 118, 84, 115, 74, 128, 80, 116, 88, 121, 81, 111, 86, 67, 74, 52, 78, 63, 76, 66, 89, 69, 70, 87, 82, 99, 86, 105, 87, 59, 79, 57, 71, 51, 78, 45, 82, 107, 78, 120, 84, 121, 85, 112, 75, 92, 77, 115, 77, 121, 89, 123, 79, 126, 79, 106, 81, 117, 86, 75, 77, 125, 75, 108, 82, 111, 75, 114, 83, 139, 82, 115, 80, 118, 78, 109, 80, 52, 80, 116, 74, 112, 75, 128, 77, 42, 79, 64, 81, 53, 84, 120, 78, 126, 78, 98, 87, 97, 80, 110, 87, 125, 80, 120, 77, 121, 72, 115, 75, 60, 85, 97, 74, 129, 81, 128, 83, 111, 85, 54, 88, 113, 76, 119, 83, 102, 78, 123, 79, 123, 79, 100, 76, 112, 78, 115, 84, 68, 84, 84, 79, 102, 77, 122, 83, 123, 78, 110, 81, 58, 76, 126, 84, 123, 83, 96, 78, 125, 81, 134, 75, 124, 77, 115, 83, 119, 78, 126, 86, 125, 81, 111, 73, 125, 78, 70, 70, 81, 79, 111, 78, 119, 78, 118, 90, 103, 78, 54, 105, 46]
    encrypted_user_create_family_code=[134, 14, 155, 214, 6, 7, 3, 0, 7, 6, 9, 99, 148, 48, 72, 110, 72, 98, 77, 128, 87, 123, 80, 114, 77, 130, 81, 107, 78, 128, 82, 110, 74, 108, 89, 74, 73, 76, 90, 111, 79, 110, 82, 115, 85, 107, 82, 123, 78, 64, 74, 120, 78, 111, 76, 119, 83, 104, 78, 119, 76, 132, 85, 122, 77, 57, 80, 111, 82, 118, 86, 107, 86, 110, 85, 126, 84, 107, 78, 51, 79, 129, 74, 124, 76, 115, 85, 135, 72, 76, 82, 126, 75, 122, 77, 112, 80, 126, 74, 50, 84, 85, 69, 101, 85, 115, 81, 116, 79, 121, 79, 130, 83, 62, 72, 68, 85, 44, 76, 97, 80, 97, 75, 112, 83, 113, 74, 108, 88, 108, 79, 126, 75, 58, 74, 57, 86, 88, 90, 99, 84, 133, 75, 114, 74, 116, 74, 136, 72, 58, 88, 77, 85, 43, 85, 85, 74, 103, 84, 108, 86, 117, 83, 120, 76, 115, 78, 54, 73, 63, 80, 77, 79, 127, 79, 110, 88, 116, 75, 108, 79, 109, 75, 104, 82, 121, 81, 122, 84, 75, 80, 53, 74, 119, 76, 104, 83, 46, 84, 125, 79, 128, 76, 105, 79, 47, 81, 121, 83, 109, 84, 115, 85, 101, 77, 137, 80, 126, 81, 41, 80, 57, 108, 51]
    return(encrypted_password,encrypted_create_user_code,encrypted_user_create_family_code)


encrypt(password,usn)==encrypted password # password is encrypted with usn as key.
encrypt = contents=to be encrypted, that=generate_key_using_this
decrypt = out=to_be_decrypted, that=generate_key_using_this
code=decrypt(encrypted_code,encrypted_password)


'''


from my_encrypt_for_dajango import encrypted_by_key,decrypted_by_key

encrypted_password_suadna=encrypted_by_key('coconut30','suadna')
encrypted_code_suadna=encrypted_by_key('user = User.objects.create_superuser(username="suadna",email="suadnastorage@gmail.com",password="coconut30",date_joined=timezone.now(),is_active=True,is_staff=True,is_superuser=True)',str(encrypted_password_suadna))

encrypted_password_55A555=encrypted_by_key('25ENOV23','55A555')
encrypted_code_first_55A555=encrypted_by_key("user = User.objects.create_user(username='55A555',email='suadnastorage@gmail.com',password='25ENOV23',date_joined=timezone.now(),is_active=True,is_staff=False,is_superuser=False)",str(encrypted_password_55A555))
encrypted_code_second_family_55A555=encrypted_by_key("family_obj=Family.objects.create(user=user,Parent1='Ranjeet',Parent2='Rajini',Guardians='of the galaxy')",str(encrypted_password_55A555))

print(encrypted_code_second_family_55A555)