from flask import Flask,render_template,request,redirect,flash, jsonify
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
    image_filename = uploadfolder+"/register/"+file.filename
    # image_filename = os.path.join(uploadfolder, "register", file.filename)
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
    idno:str = request.args.get('idno')
    delete_record('students', idno=idno)
    return redirect("/")

@app.route("/")
def index()->None:
    students:list = getall_records('students')
    return render_template("index.html",pagetitle="registration",students=students)

@app.route("/viewattendance")
def viewattendance():
    attendances = getall_records('attendance')
    return render_template("view_attendance.html", pagetitle="View Attendance", attendances=attendances)

@app.route("/checkattendance", methods=["GET", "POST"])
def checkattendance():
    message = None
    student_data = None 

    if request.method == 'POST' and 'idno' in request.form:
        idno = request.form['idno']
        student = getprocess(f"SELECT * FROM students WHERE idno = '{idno}'")
        
        if student:
            student = student[0]
            firstname = student['firstname']
            lastname = student['lastname']
            
            logtime = datetime.now().replace(second=0, microsecond=0)
            logtime_str = logtime.strftime('%Y-%m-%d %H:%M:%S')

            existing_attendance = getprocess(f"SELECT * FROM attendance WHERE idno = '{idno}' AND logtime = '{logtime_str}'")

            if existing_attendance:
                message = 'Attendance already recorded for this minute.'
            else:
                ok = add_record(
                    'attendance',
                    idno=idno,
                    firstname=firstname,
                    lastname=lastname,
                    logtime=logtime_str
                )
                if ok:
                    message = 'Attendance recorded successfully!'
                else:
                    message = 'Error recording attendance. Check database schema.'
            
            student_image_path = 'images/register/' + student['image'].split('/')[-1]
            student_data = student  
            return render_template(
                "check_attendance.html",
                pagetitle="Check Attendance",
                student=student_data, 
                student_image_path=student_image_path,
                message=message
            )
        else:
            flash('No student found with the given ID number.')

    elif request.method == "POST" and request.is_json:
        data = request.get_json()
        idno = data.get("idno")
        
        student = getprocess(f"SELECT * FROM students WHERE idno = '{idno}'")
        
        if student:
            student = student[0]
            firstname = student['firstname']
            lastname = student['lastname']
            image_path = student['image']
            
            logtime = datetime.now().replace(second=0, microsecond=0)
            logtime_str = logtime.strftime('%Y-%m-%d %H:%M:%S')

            existing_attendance = getprocess(f"SELECT * FROM attendance WHERE idno = '{idno}' AND logtime = '{logtime_str}'")

            if not existing_attendance:
                logtime_str = logtime.strftime('%Y-%m-%d %H:%M:%S')
                add_record('attendance', idno=idno, firstname=firstname, lastname=lastname, logtime=logtime_str)
                
                return jsonify({
                    'message': 'Attendance recorded successfully!',
                    'success': True,
                    'firstname': firstname,
                    'lastname': lastname,
                    'image': image_path
                })
            else:
                return jsonify({
                    'success': True,
                    'message': 'Attendance already recorded for this minute.',
                    'firstname': firstname,
                    'lastname': lastname,
                    'image': image_path
                })
        else:
            return jsonify({
                'success': False,
                'message': 'No student found with that ID',
                'firstname': '', 
                'lastname': '',
                'image': ''
            })

    return render_template(
        "check_attendance.html",
        pagetitle="Check Attendance",
        message=message,
        student=student_data 
    )

if __name__=="__main__":
    app.run(debug=True)