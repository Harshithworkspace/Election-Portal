import mysql.connector as m
from flask import Flask
import csv
import pickle
a = m.connect(
	host = "localhost",
	user = "root",
	password = "root",
                database='project'
)
cr=a.cursor()
cr1=a.cursor(buffered=True)
cr2=a.cursor()
c=1
cr.execute('DELETE FROM CANDIDATE_LIST;')
cr.execute('DELETE FROM VOTER_LIST;')
def adminlogin():
    user=input('Enter Username: ')
    pwd=input('Enter Password: ')
    cr.execute('select * from admin where Username="{}" and Password="{}";'.format(user,pwd))
    lt=[]
    for i in cr:
        lt.append(i)
    if len(lt)==1:
        return True
    else:
        print('Invalid Username and Password')
        return False
    a.commit()     
def fileupload():
    with open('D:/Harshith/Python12/SAMPLE.csv','r') as f:
        b,l,l1=csv.reader(f),[],[]
        cr.execute('Desc Candidate_list;')
        for j in cr:
            l.append(j[0].lower())
        for i in b:
            for k in range(len(i)):
                if i[k].lower()==l[k].lower():
                    sa=True
                else:
                    sa=False
            break
        if not sa:
            print('File Format Mismatch')
        for i in b:
            if sa:
                l1.append(i)
        for i in l1:
            s='Insert into candidate_list(UID,NAME,CLASS,POST) values ({},"{}","{}","{}")'.format(i[0],i[1],i[2],i[3])
            cr.execute(s)
        cr.execute('SELECT * FROM Candidate_list;')
        for i in cr:
            print(i)
    with open('D:/Harshith/Python12/SAMPLE1.csv','r') as f:
        b,ls,l2=csv.reader(f),[],[]
        cr.execute('Desc Voter_list;')
        for j in cr:
            ls.append(j[0].lower())
        for i in b:
            for k in range(len(i)):
                if i[k].lower()==ls[k].lower():
                    sa1=True
                else:
                    sa1=False
            break
        if not sa1:
            print('File Format Mismatch')
        for i in b:
            if sa1:
                l2.append(i)
        for i in l2:
            s='Insert into Voter_list(UID,NAME,CLASS) values ({},"{}",{})'.format(i[0],i[1],i[2])
            cr.execute(s)
    cr.execute('UPDATE CANDIDATE_LIST SET VOTES=0;')
    a.commit()     
def addphotos():
    cr.execute('SELECT DISTINCT POST from candidate_list;')
    global p
    p = []
    for i in cr:
        p.append(i[0])
    for i in p:
        cr.execute(f'CREATE TABLE IF NOT EXISTS {i} (UID INT PRIMARY KEY, NAME VARCHAR(75), Class VARCHAR(75), Image LONGBLOB, Voting_Classes VARCHAR(75), Votes BIGINT DEFAULT 0);')
        cr.execute(f'SELECT UID, NAME, CLASS FROM candidate_list WHERE POST="{i}";')
        dup = []
        for k in cr:
            dup.append(k)
        for j in dup:
            cr.execute(f'INSERT INTO {i} (UID, NAME, Class) VALUES (%s, %s, %s)', (j[0], j[1], j[2]))
        cr.fetchall()
        cr.execute(f'SELECT * FROM {i};')
        print(i)
        rows = cr.fetchall()
        if not rows:
            print(f"No candidates found for {i}")
            continue
        for ij in rows:
            print(ij)
            n = input('Add Photo: ')  
            with open(n, 'rb') as k:
                image_data = k.read()
                cr1.execute(f"UPDATE {i} SET Image=%s WHERE UID={ij[0]} AND NAME='{ij[1]}';", (image_data,))
            cr.fetchall()  
        cr.fetchall()
    a.commit()     
def classes():
    for i in p:
        print(i)
        vocl=input('Enter Voting Classes: ')
        cr.execute('UPDATE {} set Voting_Classes="{}";'.format(i,vocl))
    a.commit()     
def results():
    with open('Results.csv','w',newline='') as f:
        b=csv.writer(f)
        b.writerow(['RESULTS'])
        b.writerow(['POST','UID','NAME','CLASS','VOTES'])
        for i in p:
            cr.execute(f"SELECT UID, NAME, CLASS, VOTES FROM {i} WHERE VOTES = (SELECT MAX(VOTES) FROM {i});")
            res=cr.fetchall()
            for k in res:
                b.writerow((i,)+k)
        b.writerow(['OVERALL VOTES'])
        b.writerow(['UID','NAME','CLASS','POST','VOTES'])
        cr.execute("Select * from candidate_list")
        for i in cr:
            b.writerow(i)
    a.commit()     
def createuser():
    try:
        user=input('Enter Username: ')
        pwd=input('Enter Password: ')
        repwd=input('Re-enter Password: ')
        email=input('Enter Email Address: ')
        phone=int(input('Enter Phone Number: '))
        if pwd==repwd:
            cr.execute('Insert into admin values("{}","{}","{}",{});'.format(user,pwd,email,phone))
        else:
            print('Password Mismatch')
    except Exception:
        print('Account already exists')
    a.commit()     
def resetpassword():
    user=input('Enter Username: ')
    pwd=input('Enter New Password: ')
    repwd=input('Re-enter Password: ')
    email=input('Enter Email Address: ')
    phone=int(input('Enter Phone Number: '))
    cr.execute('Select USERNAME,EMAIL,PHONE_NUMBER from admin where USERNAME="{}";'.format(user))
    rp=[]
    for i in cr:
        for j in i:
            rp.append(j)
    if pwd==repwd and len(rp)!=0 and rp[0]==user and rp[1]==email and rp[2]==phone:
        cr.execute('UPDATE admin set PASSWORD="{}");'.format(pwd))
    else:
        print('User Details Mismatch')
    a.commit()     
def reports():
    cr.execute('SELECT * FROM reports WHERE STATUS IS NULL;')
    for i in cr:
        ch=int(input('Enter Choice: '))
        if ch==1:
            cr1.execute('Select VOTES from voter_list where UID={}'.format(i[0]))
            for j in cr1:
                vote=list(j[1])
                for k in vote:
                    cr2.execute('UPDATE candidate_list set VOTES=VOTES-1 where UID={};'.format(k[1]))
                    cr2.execute('UPDATE {} set VOTES=VOTES-1 where UID={};'.format(k[0],k[1]))
                    cr2.execute('UPDATE voter_list set STATUS=Null and VOTES=Null where UID={};'.format(i[0]))
                    cr2.execute('UPDATE reports set STATUS="ACCEPTED" where UID={};'.format(i[0]))
        else:
            cr2.execute('UPDATE reports set STATUS="DECLINED" where UID={};'.format(i[0]))
    a.commit()     
def admin():
    adminlogin()
    fileupload()
    addphotos()
    classes()
    voting()
    #createuser()
    #resetpassword()
def voterlogin():
    global uid
    uid=int(input('Enter UID: '))
    nam=input('Enter Name: ')
    cr.execute('select class,status from voter_list where UID={} and NAME="{}";'.format(uid,nam))
    global lt
    lt=[]
    for i in cr:
        lt.append(i)
    if len(lt)==1:
        return True
    else:
        return False                
def voting():
    if voterlogin():
        for i in lt:
            if i[1]==None :
                vote=[]
                for j in p:
                    cr.execute('Select UID,NAME,Voting_Classes from {};'.format(j))
                    voting_classes = cr.fetchall()
                    for k in voting_classes:
                        pass
                    if str(i[0]) in k[2]:
                        print(j)
                        for k in voting_classes:
                            print(k)
                        vot=int(input('Enter Choice: '))
                        vote.append([j,vot])
                        cr1.execute('UPDATE candidate_list set VOTES=VOTES+1 where UID={};'.format(vot))
                        cr1.execute('UPDATE {} set VOTES=VOTES+1 where UID={};'.format(j,vot))                       
                import json  
                vote_json = json.dumps(vote)
                cr.execute('UPDATE voter_list SET STATUS = %s, VOTES = %s WHERE UID = %s;',("VOTED", vote_json, uid))
                print('Thanks for Voting')
                rep=input('Do you want to report ?')
                if rep.lower()=='Yes'.lower():
                    cr1.execute('Insert into reports(UID,TIME) values ({},now());'.format(uid))
            else:
                print('Thanks for Voting')
                rep=input('Do you want to report ?')
                if rep.lower()=='Yes'.lower():
                    cr1.execute('Insert into reports(UID,TIME) values ({},now());'.format(uid))
    else:
        print('Invalid UID and Name')
    a.commit()     
admin()
results()
reports()
cr.close()
cr1.close()
cr2.close()
a.close()
a.commit()     
