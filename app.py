from flask import Flask,render_template,request,redirect,flash
from dbhelper import *
from icecream import ic
from datetime import datetime
import pyqrcode
import os


uploadfolder='static/images'
app = Flask(__name__)
app.config['UPLOAD_FOLDER']=uploadfolder
app.config['SECRET_KEY']='mysecretkey'


@app.route("/register",methods=['POST'])
def register()->None:
    idno:str = request.form['idno']
    lastname:str = request.form['lastname']
    firstname:str = request.form['firstname']
    course:str = request.form['course']
    level:str = request.form['level']
    
    file = request.files['uploadimage']
    image_filename = os.path.join(uploadfolder, "register", file.filename)
    file.save(image_filename)
    ic(image_filename)
    
    qrc = pyqrcode.create(idno)
    qrc_filename = uploadfolder+"/qrcode/"+idno+'.png'
    qrc.png(qrc_filename, scale=8)
    ic(qrc_filename)
    
    ok:bool = add_record('students',idno=idno,lastname=lastname,firstname=firstname,course=course,level=level,image=image_filename,qrcode=qrc_filename)
    
    message = 'error adding student'
    if ok:message = 'New Student Added'
    flash(message)
    
    return redirect("/")

@app.route("/deletestudent",methods=['GET'])
def deletestudent()->None:
    return redirect("/")

@app.route("/")
def index()->None:
    students:list = getall_records('students')
    return render_template("index.html",pagetitle="registration",students=students)

@app.route("/viewattendance")
def viewattendance():
    attendances = getall_records('attendance')
    return render_template("view_attendance.html", pagetitle="View Attendance", attendances=attendances)

@app.route("/checkattendance", methods=['GET', 'POST'])
def checkattendance():
    if request.method == 'POST':
        idno = request.form['idno']
        
        sql = f"SELECT * FROM students WHERE idno = '{idno}'"
        student = getprocess(sql)
        
        if student:
            student = student[0]
            firstname = student['firstname']
            lastname = student['lastname']
            logtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            ok = add_record(
                'attendance',
                idno=idno,
                firstname=firstname,
                lastname=lastname,
                logtime=logtime
            )
            
            if ok:
                flash('Attendance recorded successfully!')
            else:
                flash('Error recording attendance. Check database schema.')
                
            student_image_path = 'images/register/' + student['image'].split('/')[-1]
            
            return render_template(
                "check_attendance.html",
                pagetitle="check attendance",
                student=student,
                student_image_path=student_image_path
            )
        else:
            flash('No student found with the given ID number.')
    
    return render_template("check_attendance.html", pagetitle="check attendance")

if __name__=="__main__":
    app.run(debug=True)