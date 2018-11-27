from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
from flask import Flask, render_template, request, redirect, Response, url_for, session, jsonify
import random
import json
import sys

app = Flask(__name__)
app.secret_key = "super secret key"
sparql = SPARQLWrapper("http://localhost:3030/artworks/sparql")
sparql.setReturnFormat(JSON)

@app.route('/')
def output():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():

    # read the posted values from the UI
    _sparql = request.form['sparql']
    print(_sparql)
    if _sparql :
        sparql.setQuery("""
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix dbo: <http://dbpedia.org/ontology/> 
            PREFIX mdcu: <http://inf558.org/comics#>
            SELECT ?s ?o WHERE { ?s rdf:type mdcu:issue;
            mdcu:cover_date ?o. }
        """)
        sparql.setQuery(_sparql)
        results = sparql.query().convert()
        keys=results["results"]["bindings"][0].keys()
        ret=list()
        for i in range(len(results["results"]["bindings"])):
            re=list()
            for k in keys:
                re.append(results["results"]["bindings"][i][k]['value'])
            ret.append(re)
        return render_template('index.html', key=keys,result=ret)
    # else:
    #     return json.dumps({'html': '<span>Enter the required fields</span>'})
# @app.route('/receiver', methods = ['POST'])
# def signup():
#   permit='1'
#   data1 = request.json
#   if ("@" in data1['email']):
#       user= data1['email'].split("@")[0]
#       postfix=data1['email'].split("@")[1]
#       if len(data1['email'].split("@"))!=2:
#           permit='0'
#       if postfix!='usc.edu':
#           permit='0'
#       firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com', None)
#       result = firebase1.get('', None)
#       for i in result:
#           if str(i)==data1['email'].split("@")[0]:
#               permit='0'
#               break
#       if len(data1['password'])>12 or len(data1['password'])<8:
#           permit='0'
#   else: permit='0'
#   return permit


# @app.route('/login', methods = ['POST'])
# def signin():
#   permit='0'
#   data1 = request.json
#   if ("@" in data1['email']):
#       user= data1['email'].split("@")[0]
#       postfix=data1['email'].split("@")[1]
#       firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com', None)
#       result = firebase1.get(user, None)
#       if result:
#           if str(result['password'])==str(data1['password']) :
#               permit=user
#           if postfix!='usc.edu':
#               permit='0'
#           if len(data1['email'].split("@"))!=2:
#               permit='0'
#   if permit !='0':
#       session['signin'] = True
#       session['username'] = user
#   return permit


# #sign out
# @app.route('/signout')
# def signout():
#   session.clear()
#   return redirect(url_for('output'))

# @app.route('/signup')
# def redToUp():
#   return render_template('signup.html')
# @app.route('/signin')
# def redToIn():
#   return render_template('signin.html')
# @app.route('/search')
# def redToSe():
#   user=request.values.get('user')
#   return render_template('search.html',user=user)
# @app.route('/searchItem/<jsdata>', methods = ['GET'])
# def searchItems(jsdata):
    # firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
    # studentData = firebase1.get('', None)
    # firebase2 = firebase.FirebaseApplication('https://inf551usc-61ddc.firebaseio.com/', None)
    # courseData = firebase2.get('', None)
    # returnList=courseData
    # for oneCourse in returnList:
    #   will=[]
    #   for oneStudent in studentData.keys():
    #       if studentData[oneStudent].has_key('will'):
    #           for aCourse in studentData[oneStudent]['will'].keys():
    #               if studentData[oneStudent]['will'][aCourse]['courseID']==oneCourse['courseID'] and studentData[oneStudent]['will'][aCourse]['instructors']==oneCourse['courseInstructors']:
    #                   will.append(studentData[oneStudent]['email'])
    #   oneCourse['willToTutor']=will
    # return jsonify([1,2,3,4,5])

# @app.route('/fetchProfile/<jsdata>', methods = ['GET'])
# def fetchProfile(jsdata):
#   my=json.loads(jsdata)['query']
#   returnList={}
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   studentData = firebase1.get(my, None)
#   di=["History",'student',"tutor","will"]
#   li=['firstName','lastName','status','phone']
#   for i in studentData.keys():
#       if i in di:
#           temp=[]
#           for j in studentData[i].keys():
#               temp.append(studentData[i][j])
#           returnList[i]=temp
#       elif i in li:
#           returnList[i]=studentData[i]
#       else: continue
#   for i in li:
#       if returnList.has_key(i)==False:
#           returnList[i]=None
#   #for i in di:
#   #   if returnList.has_key(i)==False:
#   #       returnList[i]="n"

#   return jsonify(returnList)


# @app.route('/restPWD', methods = ['POST'])
# def restPWD():
#   oldPWD=request.form['oldPWD'];
#   newPWD=request.form['newPWD'];
#   conPWD=request.form['conPWD'];
#   my=request.form['my'];
#   if newPWD==conPWD:
#       firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#       old=firebase1.get(my, "password")
#       # print type(oldPWD),type(old)
#       if str(oldPWD)==str(old):
#           firebase1.put(my, "password",newPWD)
#           return 'success'
#   return "fail"
# @app.route('/updateProfile', methods = ['POST'])
# def updateProfile():
#   firstName=request.form['firstName'];
#   lastName=request.form['lastName'];
#   status=request.form['status'];
#   phone=request.form['phone'];
#   my=request.form['my'];
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   firebase1.put(my,"firstName", firstName)
#   firebase1.put(my,"lastName", lastName)
#   firebase1.put(my,"status", status)
#   firebase1.put(my,"phone", phone)
#   return 'success'
# @app.route('/tutorAdd', methods = ['POST'])
# def tutorAdd():
#   courseID=request.form['courseInf'].split('_')[0]
#   instructors=request.form['courseInf'].split('_')[1]
#   tutorEmail=request.form['tutorEmail']
#   my=request.form['my']
#   # print courseID,instructors,tutorEmail,my
#   if tutorEmail!="Not selected":
#       firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#       tutor=tutorEmail.split('@')[0]
#       tutors=firebase1.get(my,'tutor');
#       students=firebase1.get(tutor,'student');
#       exist=False
#       if students!=None:
#           for i in students.keys():
#               if (students[i]['courseID']==courseID and students[i]['instructors']==instructors and students[i]['email']==my+"@usc.edu") or my==tutor:
#                   exist=True
#                   break
#       if exist==False and tutor!=my:
#           firebase1.post(tutor+'/student', {'courseID':courseID,'instructors':instructors,'email':my+"@usc.edu"})
#           firebase1.post(my+'/tutor', {'courseID':courseID,'instructors':instructors,'email':tutor+"@usc.edu"})
#           return "success"
#   return "fail"

# @app.route('/willAdd', methods = ['POST'])
# def willAdd():
#   courseID=request.form['courseInf'].split('_')[1]
#   instructors=request.form['courseInf'].split('_')[2]
#   my=request.form['my']
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   wills=firebase1.get(my,'will')
#   exist=False
#   if wills!=None:
#       for i in wills.keys():
#           if wills[i]['courseID']==courseID and wills[i]['instructors']==instructors:
#               exist=True
#               break
#   if exist==False:
#       firebase1.post(my+'/will', {'courseID':courseID,'instructors':instructors})
#       return 'success'
#   return "fail"

# @app.route('/HistoryDel', methods = ['POST'])
# def hisDel():
#   my=request.form['my']
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   firebase1.delete(my,'History')
#   return "success"


# @app.route('/willDel', methods = ['POST'])
# def willDel():
#   courseID=request.form['courseID']
#   instructors=request.form['instructors']
#   my=request.form['my']
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   wills=firebase1.get(my,'will')
#   for i in wills.keys():
#       if wills[i]['courseID']==courseID and wills[i]['instructors']==instructors:
#           students=firebase1.get(my,'student');
#           if students!=None:
#               for j in students.keys():
#                   if students[j]['courseID']==courseID and students[j]['instructors']==instructors:
#                       tutor=students[j]['email'].split('@')[0]
#                       tutors=firebase1.get(tutor,'/tutor')
#                       for k in tutors.keys():
#                           if tutors[k]['courseID']==courseID and tutors[k]['instructors']==instructors and tutors[k]['email']==my+'@usc.edu':
#                               firebase1.delete(tutor+'/tutor',k)
#                               break
#                       firebase1.delete(my+'/student',j)
#               firebase1.delete(my+'/will',i)
#           return "success"
#   return "fail"

# @app.route('/tutorDel', methods = ['POST'])
# def tutorDel():
#   courseID=request.form['courseID']
#   instructors=request.form['instructors']
#   tutorEmail=request.form['tutorEmail']
#   my=request.form['my']
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   tutors=firebase1.get(my,'tutor')
#   for i in tutors.keys():
#       if tutors[i]['courseID']==courseID and tutors[i]['instructors']==instructors and tutors[i]['email']==tutorEmail:
#           tutor=tutorEmail.split('@')[0]
#           students=firebase1.get(tutor,'student')
#           for j in students.keys():
#               # print j
#               if students[j]['courseID']==courseID and students[j]['instructors']==instructors and students[j]['email']==my+"@usc.edu":
#                   # print "1234",j
#                   firebase1.delete(tutor+'/student',j)
#                   break
#           firebase1.delete(my+'/tutor',i)
#           return "success"
#   return "fail"
# @app.route('/stuDel', methods = ['POST'])
# def stuDel():
#   courseID=request.form['courseID']
#   instructors=request.form['instructors']
#   stuEmail=request.form['stuEmail']
#   my=request.form['my']
#   # print my
#   firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#   stus=firebase1.get(my,'student')
#   for i in stus.keys():
#       if stus[i]['courseID']==courseID and stus[i]['instructors']==instructors and stus[i]['email']==stuEmail:
#           stu=stuEmail.split('@')[0]
#           tutors=firebase1.get(stu,'tutor')
#           for j in tutors.keys():
#               if tutors[j]['courseID']==courseID and tutors[j]['instructors']==instructors and tutors[j]['email']==my+"@usc.edu":
#                   firebase1.delete(stu+'/tutor',j)
#                   break
#           firebase1.delete(my+'/student',i)
#           return "success"
#   return "fail"

# @app.route('/upHist', methods = ['POST'])
# def upHist():
#   if request.form['upHist']!="":
#       firebase1 = firebase.FirebaseApplication('https://inf551uscstudent.firebaseio.com/', None)
#       firebase1.post(request.form['user']+'/History', request.form['upHist'])
#   return "received"

# class ProfileEdit(Form):
#   email = StringField("Email", [validators.Length(min = 1, max = 50)])
#   name  = StringField("Full Name", [validators.Length(min = 1, max = 30)])
#   Cur_Pwd = StringField("Current Password",[validators.Length(min = 8, max = 12)])
#   New_pwd1 = StringField("New Password",[validators.Length(min = 8, max = 12)])
#   New_pwd2 = StringField("Confirm New Password",[
#           validators.DataRequired(),
#           validators.EqualTo('New Password', message = 'Passwords do not match')
#       ])
#   Tut_info = StringField("Your Tutor Info")
#   Stu_info = StringField("Your Student Info")

# @app.route('/profile', methods=['GET','POST'])
# def redToProfile():
#   form = ProfileEdit(request.form)
#   if request.method == 'POST' and form.validate():
#       email = form.email.data
#       name = form.name.data
#       Cur_Pwd = form.Cur_Pwd.data
#       New_pwd1 = form.New_pwd1.data
#       New_pwd2 = form.New_pwd1.data

#       form = FirePut()
#       if form.validate_on_submit():
#           putData = {}
#       return render_template('profile.html')
#   return render_template('profile.html', form=form)
# @app.route('/reset_pwd')
# def rest_pass():
#   return render_template('reset_pwd.html')


if __name__ == '__main__':
    app.run(debug=True)


