import os
import cx_Oracle
from flask import Flask
from flask import Flask,render_template, redirect, url_for, request, g, Blueprint,jsonify,session
from flask_login import login_required
from flask_login import current_user, login_user, logout_user
#from models import User
from flask_login import LoginManager, UserMixin
#from form import LoginForm
from collections import defaultdict
from passlib.hash import sha256_crypt

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

#gloabl variable that needs to be changed each semester
currentsemester = 'fa2021'

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def app_loader():
    return redirect('/login') 

@app.route('/home')
def home_loader():
    if session.get('email') == None:
        return redirect('/login')

    return render_template("home.html")

@app.route('/invalid')
def invalid_loader():
    return render_template("invalid.html")

@app.route('/createAccount')
def create_acc_loader():
    return render_template('createacct.html')

@app.route('/errorCreateAccount')
def error_create_account():
    return render_template('errorCreateAccount.html')

@app.route('/browse')
def browse_loader():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('browse.html')

#handler for updating account info
@app.route('/updateAccountAction',methods=["GET","POST"])
def updateAction():
    if session.get('email') == None:
        return redirect('/login')

    regtime = request.form.get('regTime')
    #could be 08:30 or 08:30:00
    splitreg = regtime.split(':')
    regtime = (splitreg[0]+splitreg[1]).lstrip('0')
    password = request.form.get('password')
    passwordHash = sha256_crypt.hash(password)
    privacy = request.form.get('privacy')

    cur = connect2db()
    email=session['email']

    #update db with new info
    if regtime != "":
        cur.execute("update userinfo set regtime = :r where email = :e ",r=regtime,e=email)
    if password != "":
        cur.execute("update userinfo set password = :p where email = :e ", p=passwordHash,e=email)
    if privacy != "":
        cur.execute("update userinfo set privacy = :pp where email = :e ", pp=privacy, e=email)


    q1 = "select regtime from userinfo where email='{}'".format(email)
    cur.execute(q1)
    currReg = str(cur.fetchone()[0])

    sendReg = ""
    if len(currReg) == 3:
        #stored as 730, need to turn into 7:30:00
        sendReg = "0" + currReg[0] + ":" + currReg[1:] + ":00"
    else:
        #stored as 1220,need to turn into 12:20:00
        sendReg = currReg[0] + currReg[1] + ":" + currReg[2:] + ":00"


    q2 = "select privacy from userinfo where email='{}'".format(email)
    cur.execute(q2)
    currP = cur.fetchone()[0]

    privStat=""
    if currP == "private":
        privStat="Private"
    else:
        privStat = "Public"

    return render_template("updateAccount.html", currReg=sendReg, message="Account updated successfully",privacy=privStat)

#handler for create account
@app.route('/addAccount', methods=['GET', 'POST'])
def addAccount():
    #get info from html page
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    privacy = request.form['privacy']
    regTime = request.form['regTime'].replace(':','')
    gradYear = request.form['gradYear']
    accountType="student"

    #DATABASE ACCESS & ANALYSIS
    cur = connect2db()

    #get current list of user accounts
    cur.execute('''SELECT email from userInfo''')
    res = cur.fetchall()

    userAccountsCurrent = []
    for row in res:
        userAccountsCurrent.append(row[0])

    #make sure email hasn't already been used bc email is the primary key
    if email in userAccountsCurrent:
        #error and prompt user to either login or enter a different email
        return redirect('/errorCreateAccount')

    #hash password for security -- 64 chars sha 256
    passwordHash = sha256_crypt.hash(password)

    #insert command in mysql for the new account
    cur.execute("INSERT INTO userInfo (email, password, accounttype, privacy, regtime, names, gradyear) VALUES (:em,:pas,:acc,:priv,:reg,:n,:year)",em=email,pas=passwordHash,acc=accountType,priv=privacy,reg=regTime,n=name,year=gradYear)

    session['email'] = email
    return redirect('/home')


#handle user login authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    session['email'] = None

    userAccounts = defaultdict(lambda:"Not Present")
    userAccounts['landone'] = 'admin'

    if request.method == 'GET':
        return render_template('login.html')

    #DATABASE ACCESS & ANALYSIS
    cur = connect2db()

    #query to get dict of usernames and passwords
    cur.execute('''SELECT * from userInfo''')
    accounts = cur.fetchall()

    #put infor into user accounts
    for row in accounts:
        userAccounts[row[0]] = row[1]

     #validate user login
    usernameEntry = request.form['email']
    session['email'] = request.form['email']
    if usernameEntry in list(userAccounts.keys()):
        #verify hashed password
        if sha256_crypt.verify(request.form['password'], userAccounts[usernameEntry]):     
            '''user = User()
            user.id = usernameEntry
            login_user(user)'''
            return redirect('/home')
        else:
            #password did not match username
            #bad login attempt
            return redirect('/invalid')
    else:
        #not a valid username
        #bad login attempt
        return redirect('/invalid')

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@app.route('/ratecourse')
def ratecourse():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('ratecourse.html')

@app.route('/ratespecificcourse')
def ratespecificcourse():
    if session.get('email') == None:
        return redirect('/login')

    url = request.url.split('?')[1]
    coursename = url.replace('%20',' ').replace("%27","'").replace("%2F","/").replace("%40","@")
    coursename2 = url.split('--%20')[1]
    return render_template('rate_c.html',coursename=coursename,coursename2=coursename2)

@app.route('/addcourseratings',methods=['GET','POST'])
def addcourseratings():
    if session.get('email') == None:
        return redirect('/login')

    coursename = request.form['submit'].replace('%20',' ').replace("%27","'").replace("%2F","/").replace("%40","@")
    overall = request.form.get('overall')
    usefulness = request.form.get('usefulness')
    workload = request.form.get('workload')
    difficulty = request.form.get('difficulty')
    enjoyment = request.form.get('enjoyment')
    comments = request.form.get('comments')
    email = session['email']
    if request.form.get('takeagain') == 'on':
        takeagain = '1'
    else:
        takeagain = '0'
    cur = connect2db()
    cur.execute("merge into ratescourse dest using (select :e email,:cname coursename,:useful usefulness,:work workload,:diff difficulty,:enj enjoyment,:comm comments, :take takeagain,:ov overall from dual) src on (dest.email=src.email and dest.coursename=src.coursename) when matched then update set usefulness = src.usefulness,workload=src.workload,difficulty=src.difficulty,enjoyment=src.enjoyment,comments=src.comments,takeagain=src.takeagain,overall=src.overall when not matched then insert(email,coursename,usefulness,workload,difficulty,enjoyment,comments,takeagain,overall) values (src.email,src.coursename,src.usefulness,src.workload,src.difficulty,src.enjoyment,src.comments,src.takeagain,src.overall)",e=email,cname=coursename,useful=usefulness,work=workload,diff=difficulty,enj=enjoyment,comm=comments,take=takeagain,ov=overall)
    return render_template('ratingsubmitted.html')

@app.route("/livesearchcourse",methods=["POST","GET"])
def livesearchcourse():
    if session.get('email') == None:
        return redirect('/login')

    searchbox = request.form.get("text").lower()
    cursor = connect2db()
    cursor.execute("select distinct n || ' -- ' || coursename att from (select coursename,substr(coursenum,1,instr(coursenum,'-')-1) n from Course where lower(coursenum) LIKE '%'||:myvar||'%' or lower(coursename) like '%'||:myvar||'%' order by coursename,coursenum) order by att",myvar=searchbox)
    result = cursor.fetchall()
    return jsonify(result)

@app.route("/rateprof")
def rateprof():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('rateprof.html')

@app.route("/livesearchprofname",methods=["POST","GET"])
def livesearchprofname():
    if session.get('email') == None:
        return redirect('/login')

    searchbox = request.form.get("text")
    cursor = connect2db()
    cursor.execute("select distinct profname from Professor where lower(profname) LIKE '%'||:myvar||'%' order by profname",myvar=searchbox)
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/ratespecificprof')
def ratespecificprof():
    if session.get('email') == None:
        return redirect('/login')

    profname = request.url.split('?')[1].replace('%20',' ')
    cur = connect2db()
    #don't need to bind -> var taken from url
    query = "select profid from Professor where profname like '{}'".format(profname)
    cur.execute(query)
    profid = cur.fetchone()[0]
    return render_template('rate_p.html',profid=profid,profname=profname)

@app.route('/addprofratings',methods=["POST","GET"])
def addprofratings():
    if session.get('email') == None:
        return redirect('/login')

    profid = request.form['submit']
    overall = request.form.get('overall')
    style = request.form.get('style')
    approach = request.form.get('approach')
    email = session['email']
    if request.form.get('takeagain') == 'on':
        takeagain = '1'
    else:
        takeagain = '0'
    comments = request.form.get('comments')
    cur = connect2db()
    cur.execute("merge into ratesprofessor dest using (select :e email,:pid profid,:s teachingstyle,:app approachability,:comm comments,:take takeagain,:ov overall from dual) src on (dest.email=src.email and dest.profid=src.profid) when matched then update set teachingstyle = src.teachingstyle,approachability=src.approachability,comments=src.comments,takeagain=src.takeagain,overall=src.overall when not matched then insert(email,profid,teachingstyle,approachability,comments,takeagain,overall) values (src.email,src.profid,src.teachingstyle,src.approachability,src.comments,src.takeagain,src.overall)",e=email,pid=profid,s=style,app=approach,comm=comments,take=takeagain,ov=overall)
    return render_template('ratingsubmitted.html')


@app.route('/seeprof')
def seeprof():
    if session.get('email') == None:
        return redirect('/login')

    url=request.url
    profname = request.url.split('?')[1].replace('%20',' ')
    cur = connect2db()
    #don't need to bind - variable taken from url
    scorequery = "select overall, style, approach,num,again from (select profid pid, avg(overall) overall,avg(teachingstyle) style,avg(approachability) approach,count(*) num,sum(takeagain) again from ratesprofessor group by profid),professor where professor.profid = pid and profname ='{}'".format(profname)
    cur.execute(scorequery)
    result = cur.fetchall()

    #no ratings
    if len(result) == 0:
        courses = getcoursestaught(profname,cur)
        return render_template('profpage.html',profname=profname,overall="--",style="--",approach="--",takeagain="--",comments=[("--","--")],courses=courses,semester=getsemester(currentsemester),url=url)

    overall = round(result[0][0],1)
    style = round(result[0][1],1)
    approach = round(result[0][2],1)
    takeagain = round(float(result[0][4])*100/float(result[0][3]),1)

    #don't need to bind,profname taken from url
    indvquery = "select overall,teachingstyle,approachability,takeagain,comments from ratesprofessor,professor where ratesprofessor.profid = professor.profid and profname='{}'".format(profname)
    cur.execute(indvquery)
    individual=cur.fetchall()
    courses = getcoursestaught(profname,cur)
    return render_template('profpage.html',profname=profname,overall=overall,style=style,approach=approach,takeagain=takeagain,individual=individual,courses=courses,semester=getsemester(currentsemester),url=url)

def getcoursestaught(profname,cur):
    #don't need to bind, profname taken from url
    query = "select coursename,coursenum,course.crn,credits,seats,dateandtime,location,'http://52.87.107.120:8022/seecourse?' || replace(coursenum,' ','%20') || '%20--%20' || replace(coursename,' ','%20') from course,professor,teaches where profname='{}' and professor.profid=teaches.profid and teaches.crn=course.crn and course.semester='{}' order by coursename".format(profname,currentsemester)
    cur.execute(query)
    return cur.fetchall()

@app.route('/seecourse')
def seecourse():
    if session.get('email') == None:
        return redirect('/login')

    url = request.url
    coursename=request.url.split('--%20')[1].replace('%20',' ').replace("%27","'").replace("%2F","/").replace("%40","@")
    coursenameurl = request.url.split('?')[1].replace('%20',' ').replace("%27","'").replace("%2F","/").replace("%40","@")
    cur = connect2db()
    #don't need to bind,coursename taken from url
    query = "select round(avg(overall),1) overall, round(avg(usefulness),1) useful, round(avg(workload),1) work, round(avg(difficulty),1) dif, round(avg(enjoyment),1),sum(takeagain) take, count(*) num,coursename from ratescourse where coursename = '{}' group by coursename".format(coursename.replace("'","''"))
    cur.execute(query)
    result = cur.fetchall()

    if len(result) == 0:
        result=["--","--","--","--","--","--","--"]
        comments=[("--","--")]
        courses=getcourses(coursename,cur)
        return render_template('coursepage.html',coursename=coursename,result=result,takeagain="--",comments=comments,courses=courses,url=url,semester=getsemester(currentsemester))

    takeagain=round(float(result[0][5])*100/float(result[0][6]),1)
    #don't need to bind, coursename taken from url
    indvquery = "select overall,usefulness,workload,difficulty,enjoyment,takeagain,comments from ratescourse where coursename = '{}'".format(coursename)
    cur.execute(indvquery)
    individual = cur.fetchall()

    courses = getcourses(coursename,cur)

    return render_template('coursepage.html',coursename=coursename,result=result[0],takeagain=takeagain,individual=individual,courses=courses,url=url,semester=getsemester(currentsemester))

def getcourses(coursename,cur):
    #don't need to bind,coursename taken from url
    coursequery = "select coursenum,course.crn,credits,seats,dateandtime,location,profname,'http://52.87.107.120:8022/seeprof?' || replace(profname,' ','%20') from course,professor,teaches where coursename='{}' and course.semester='{}' and course.crn=teaches.crn and teaches.profid=professor.profid order by coursenum".format(coursename.replace("'","''"),currentsemester)
    cur.execute(coursequery)
    return cur.fetchall()

@app.route('/profleaderboard')
def profleaderboard():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('profleaderboard.html')

@app.route('/getprofleaderboard',methods=["POST","GET"])
def getprofleaderboard():
    if session.get('email') == None:
        return redirect('/login')

    dept = request.form.get('dept')
    rankby = request.form.get('rankby')
    cur = connect2db()
    columns = ["Professor","Department(2)","","# Ratings"]

    if rankby == "overall":
        description = "Best to Worst Overall Professors"
    elif rankby == "teachingstyle":
        columns[2] = "Average Teaching Style Score"
        description = "Best to Worst Teaching Styles"
    elif rankby == "approachability":
        description = "Most to Least Approachable Professors"

    if dept == "any":
        columns = ["Professor","Department(s)","","# Ratings"]
        query = profquery(rankby)
        columns[2] = gencolname(rankby)

    elif dept is None:
        return render_template('profleaderboard.html')

    else:
        dept = dept.upper()
        columns = ["Professor","Department","","# Ratings"]
        query = profquerydept(dept,rankby)
        columns[2] = gencolname(rankby)

    cur.execute(query)
    result = cur.fetchall()
    return render_template("displayprofleaderboard.html",columns=columns,result=result,description=description)


#variables in these functions come from dropdowns so don't need to bind - user can't sql inject
def profquery(attr):
    return "select profname,depts,av,num from (select profname,pid,listagg(deptname,', ') within group(order by deptname) depts from (select profname, deptname,professor.profid pid from professor,professorisin,department where professor.profid=professorisin.profid and professorisin.did=department.did) group by profname,pid),(select round(avg({}),1) av,count(*) num,profid ppid from ratesprofessor group by profid) where ppid=pid order by av desc,num desc,profname".format(attr)

def profquerydept(dept,attr):
    return  "select profname,'{}',av,num from (select profid pid from (select did ddid from department where deptname='{}'),professorisin where ddid=professorisin.did),(select round(avg({}),1) av,count(*) num,profid ppid from ratesprofessor group by profid),professor where ppid=pid and ppid=professor.profid order by av desc,num desc,profname".format(dept,dept,attr)


@app.route('/courseleaderboard')
def courseleaderboard():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('courseleaderboard.html')

@app.route('/getcourseleaderboard',methods=["POST","GET"])
def getcourseleaderboard():
    if session.get('email') == None:
        return redirect('/login')

    dept = request.form.get('dept')
    rankby = request.form.get('rankby')
    cur = connect2db()

    if rankby == "overall":
        description = "Best to Worst Overall Courses"
    elif rankby == "usefulness":
        description = "Most to Least Useful Courses"
    elif rankby == "workload":
        description = "Most to Least Chill Courses"
    elif rankby == "difficulty":
        description = "Easiest to Hardest Courses"
    elif rankby == "enjoyment":
        description = "Most to Least Enjoyable Courses"

    if dept == "any":
        columns=["Course Name","Course Number(s)","","# Ratings"]
        query = coursequery(rankby)
        columns[2] = gencolname(rankby)

    elif dept is None:
        return render_template('courseleaderboard.html')
    else:
        dept = dept.upper()
        columns = ["Course Name","Course Number(s)","","# Ratings"]
        query = coursequerydept(rankby,dept)
        columns[2] = gencolname(rankby)

    cur.execute(query)
    result = cur.fetchall()
    return render_template("displaycourseleaderboard.html",columns=columns,result=result,description=description)

#vars in these functions come from dropdowns - don't need to bind because no place for injection
def coursequery(attr):
    return  "select a.coursename,coursenum,av,num from (select coursename,round(avg({}),1) av,count(*) num from ratescourse group by coursename) a ,(select coursename,listagg(cnum,', ') within group(order by coursename) coursenum from (select distinct coursename, substr(coursenum, 1, instr(coursenum, '-') -1) cnum from course) group by coursename) b where a.coursename = b.coursename order by av desc,num desc,a.coursename".format(attr)

def coursequerydept(attr,dept):
    return "select a.coursename,coursenum,av,num from (select coursename,round(avg({}),1) av,count(*) num from ratescourse group by coursename) a ,(select coursename,listagg(cnum,', ') within group(order by coursename) coursenum from (select distinct coursename, substr(coursenum, 1, instr(coursenum, '-') -1) cnum from course where coursenum like '%{}%') group by coursename) b where a.coursename = b.coursename order by av desc,num desc,a.coursename".format(attr,dept)

def gencolname(s):
    return s + " score"

@app.route('/addcoursetolist',methods=["GET","POST"])
def addcoursetolist():
    if session.get('email') == None:
        return redirect('/login')

    url = request.form['submit'].split('@#$')[0]
    coursenum = request.form['submit'].split('@#$')[1]
    category = request.form.get('category')
    email = session['email']
    cur = connect2db()
    #coursenum comes from url so don't need to bind
    q = "select crn from course where semester='{}' and coursenum='{}'".format(currentsemester,coursenum)
    cur.execute(q)
    crn = cur.fetchone()[0]
    cur.execute("merge into choosescourse dest using (select :e email,:c crn,:sem semester,:cat category from dual) src on (dest.email=src.email and dest.crn=src.crn and dest.semester=src.semester) when matched then update set category=src.category when not matched then insert(email,crn,semester,category) values (src.email,src.crn,src.semester,src.category)",e=email,c=crn,sem=currentsemester,cat=category)
    return redirect(url,code=302)

@app.route('/removecoursefromlist',methods=["GET","POST"])
def removecoursefromlist():
    if session.get('email') == None:
        return redirect('/login')

    email = session['email']
    crn = request.form['submit']
    cur = connect2db()
    cur.execute("delete from choosescourse where email=:e and crn=:c and semester=:s",e=email,c=crn,s=currentsemester)
    return redirect('/myschedule',code=302)

@app.route('/myschedule',methods=["GET","POST"])
def myschedule():
    if session.get('email') == None:
        return redirect('/login')

    email = session['email']
    cur = connect2db()
    #don't need to bind, no user inputs
    cur.execute("select coursename,coursenum,course.crn,seats,location,dateandtime,credits,profname,category from course,choosescourse,professor,teaches where course.crn = choosescourse.crn and course.semester=choosescourse.semester and professor.profid=teaches.profid and teaches.crn=course.crn and teaches.semester=course.semester and choosescourse.semester='{}' and choosescourse.email='{}' and category='Definitely' order by dateandtime".format(currentsemester,email))
    defcourses = cur.fetchall()
    cur.execute("select coursename,coursenum,course.crn,seats,location,dateandtime,credits,profname,category from course,choosescourse,professor,teaches where course.crn = choosescourse.crn and course.semester=choosescourse.semester and professor.profid=teaches.profid and teaches.crn=course.crn and teaches.semester=course.semester and choosescourse.semester='{}' and choosescourse.email='{}' and category='Maybe' order by dateandtime".format(currentsemester,email))
    maybecourses = cur.fetchall()
    return render_template('myschedule.html',defcourses=defcourses,maybecourses=maybecourses,semester=getsemester(currentsemester))

@app.route('/searchfriends',methods=["GET","POST"])
def searchfriends():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('searchfriends.html')

@app.route("/livesearchemail",methods=["POST","GET"])
def livesearchemail():
    if session.get('email') == None:
        return redirect('/login')

    searchbox = request.form.get("text").lower()
    myemail= session['email']
    cursor = connect2db()
    cursor.execute("select email from userinfo where privacy='public' and accounttype='student' and lower(email) like '%'||:s||'%' and email != :e order by email ",s=searchbox,e=myemail)
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/friendschedule',methods=["GET","POST"])
def friendschedule():
    if session.get('email') == None:
        return redirect('/login')

    url = request.url
    email_f = request.url.split('?')[1].replace('%40','@')
    cur = connect2db()
    name="select names from userinfo where email='{}' ".format(email_f)
    cur.execute(name)
    n = cur.fetchone()[0]
    #don't need to bind these because var comes from url
    q = "select coursename,coursenum,course.crn,seats,location,dateandtime,credits,profname,category from course,choosescourse,professor,teaches where course.crn = choosescourse.crn and course.semester=choosescourse.semester and professor.profid=teaches.profid and teaches.crn=course.crn and teaches.semester=course.semester and choosescourse.semester='{}' and choosescourse.email='{}' and category='Definitely' order by dateandtime".format(currentsemester,email_f)
    cur.execute(q)
    defcourses=cur.fetchall()
    q = "select coursename,coursenum,course.crn,seats,location,dateandtime,credits,profname,category from course,choosescourse,professor,teaches where course.crn = choosescourse.crn and course.semester=choosescourse.semester and professor.profid=teaches.profid and teaches.crn=course.crn and teaches.semester=course.semester and choosescourse.semester='{}' and choosescourse.email='{}' and category='Maybe' order by dateandtime".format(currentsemester,email_f)
    cur.execute(q)
    maybecourses=cur.fetchall()

    return render_template('friendschedule.html',defcourses=defcourses,maybecourses=maybecourses,semester=getsemester(currentsemester),n=n,url=url)

@app.route('/livesearchcourseall',methods=["GET","POST"])
def livesearchcourseall():
    if session.get('email') == None:
        return redirect('/login')

    searchbox = request.form.get("text").lower()
    cursor = connect2db()
    cursor.execute("select distinct coursenum || ' -- ' || coursename n from Course where lower(coursenum) LIKE '%'||:s||'%' or lower(coursename) like '%'||:s||'%' order by n",s=searchbox)
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/probsearch')
def probsearch():
    if session.get('email') == None:
        return redirect('/login')

    return render_template('probcourse.html')

@app.route('/calculateprobability',methods=["GET","POST"])
def calculateprobability():
    if session.get('email') == None:
        return redirect('/login')

    coursenum = request.url.split('?')[1].split('%20')[0];
    myemail = session['email']
    cur = connect2db()
    #don't need to bind - coursenum comes from url
    q = "select crn,seats from course where coursenum = '{}' ".format(coursenum)
    cur.execute(q)
    result = cur.fetchone()
    crn = result[0]
    seats = int(result[1])
    #don't need to bind - no user inputs
    regq = "select regtime from userinfo where email= '{}'".format(myemail)
    cur.execute(regq)
    mytime = cur.fetchone()[0]
    #don't need to bind these, no user inputs
    qdef = "select count(*) num from choosescourse,userinfo where choosescourse.email=userinfo.email and userinfo.regtime < '{}' and crn='{}' and semester='{}' and category='Definitely' ".format(mytime,crn,currentsemester)
    cur.execute(qdef)
    numdef=int(cur.fetchone()[0])
    qmaybe = "select count(*) num from choosescourse,userinfo where choosescourse.email=userinfo.email and userinfo.regtime < '{}' and crn='{}' and semester='{}' and category='Maybe' ".format(mytime,crn,currentsemester)
    cur.execute(qmaybe)
    nummaybe=int(cur.fetchone()[0])

    together = numdef+nummaybe

    if seats <= numdef:
        chances = "low"
    elif seats <= together:
        chances = "average"
    elif seats > together:
        chances = "high"

    return render_template('probresult.html',chances=chances,coursenum=coursenum,numdef=numdef,nummaybe=nummaybe,seats=seats)

@app.route('/updateAccount')
def updateAccount():
    if session.get('email') == None:
        return redirect('/login')

    cur = connect2db()
    email=session['email']

    q1 = "select regtime from userinfo where email='{}'".format(email)
    cur.execute(q1)
    currReg = str(cur.fetchone()[0])

    sendReg = ""
    if len(currReg) == 3:
        #stored as 730, need to turn into 7:30:00
        sendReg = "0" + currReg[0] + ":" + currReg[1:] + ":00"
    else:
        #stored as 1220,need to turn into 12:20:00
        sendReg = currReg[0] + currReg[1] + ":" + currReg[2:] + ":00"

    q2 = "select privacy from userinfo where email='{}'".format(email)
    cur.execute(q2)
    currP = cur.fetchone()[0]

    privStat=""
    if currP == "private":
        privStat="Private"
    else:
        privStat = "Public"

    return render_template('updateAccount.html',currReg=sendReg,message="",privacy=privStat)

def getsemester(currentsemester):
    s = currentsemester[:2]
    if s == "fa":
        sem = "Fall"
    elif s == "sp":
        sem = "Spring"
    else:
        sem = "Summer"

    return sem + ' ' + currentsemester[-4:]

def connect2db():
    dsn_tns = cx_Oracle.makedsn('ip-172-22-135-206', '1521', service_name='XE')
    connection = cx_Oracle.connect('hr','hr',dsn=dsn_tns)
    connection.autocommit = True
    cur = connection.cursor()
    return cur

if __name__ == '__main__':
      app.run(host='0.0.0.0', port='8022')

