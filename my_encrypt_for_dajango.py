
def delete_file(file):
    import os
    os.remove(f'{file}.dat')


def generate_key(source_obj):
    #the numbers in this function are experimental and do not hold special significance.
    import random

    key=''
    for i in source_obj:
        for j in range(ord(i)*2):

            random.seed(j)
            t=str(random.randint(0,1000))
            key+=t

    random.seed(ord(key[0])+int(key[-1]))
    t=random.randint(0,len(key)//2)
    key=key[t::]

    if len(key)>2000:
        key=key[0:2000]

    return(key)


class encrypt():
    def fill_list_with_ascii_of_contents(contents):
        out_list=[]
        
        for i in contents:
            out_list.append(ord(i))
        return(out_list)
        
    def pickle_list_here(list_to_encrypt,location):
        import pickle

        file=open(f'{location}.dat','wb')
        pickle.dump(list_to_encrypt,file)
        file.close()
        
    def get_raw_pickled_data_from(location):
        file=open(f'{location}.dat','r',encoding='iso-8859-15')
        contents=file.read()
        file.close()

        return contents

def get_number_to_add(key,count,odd_or_even,check):
        try:
            number_to_add = int(key[count]) 
        except IndexError:
            count = 0
            number_to_add = int(key[count])
        count+=1

        if odd_or_even%2==check:
            number_to_add=0-number_to_add

        return(number_to_add,count)

def substitute(key,outgoing_list,check):
    count=0
    #most numbers here are experimental and hold no special significance.
    for i in range(int(key[1])):
        for j in range(len(outgoing_list)):
            number_to_add,count=get_number_to_add(key,count,i,check) #check=1 for encrypt, check=0 for decrypt
            outgoing_list[j]=outgoing_list[j]+number_to_add
    return(outgoing_list)

def encrypted_by_key(contents,key):
    key=generate_key(key)
    final_changing_list = encrypt.fill_list_with_ascii_of_contents(contents)
    
    final_changing_list = substitute(key,final_changing_list,1)

    encrypt.pickle_list_here(final_changing_list,'store')
    contents=encrypt.get_raw_pickled_data_from('store')

    final_changing_list=encrypt.fill_list_with_ascii_of_contents(contents)

    final_changing_list=substitute(key[::-1],final_changing_list,1)#reversing key has no specifial significance. 

    delete_file('store')

    return(final_changing_list)
    
class decrypt():
    def get_unpickled_data_from(Location):
        import pickle
        try:
            file=open(f'{Location}.dat','rb')
            outgoing_list=pickle.load(file)
            file.close()
        except FileNotFoundError:
            print("Wrong username or password.")
            exit()
        
        return(outgoing_list)
    
    def get_characters_of_ascii_list(given_list):
        data=''
        for i in given_list:
            data+=str(chr(i))
        
        return(data)
    
    def write_data_in(data,Location):
        file=open(f'{Location}.dat','w',encoding='iso-8859-15')
        file.write(data)
        file.close()

def decrypted_by_key(final_changing_list,key): 
    import pickle
    key=generate_key(key)

    final_changing_list = substitute(key[::-1],final_changing_list,0)

    content = decrypt.get_characters_of_ascii_list(final_changing_list)

    decrypt.write_data_in(content,'store')
    final_changing_list = decrypt.get_unpickled_data_from('store')

    final_changing_list = substitute(key,final_changing_list,0)
    
    content = decrypt.get_characters_of_ascii_list(final_changing_list)

    delete_file('store')

    return(content)
