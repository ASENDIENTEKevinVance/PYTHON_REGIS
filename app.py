from flask import Flask,render_template,request,redirect,flash
from dbhelper import *
from icecream import ic
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
def viewattendance()->None:
    return render_template("view_attendance.html",pagetitle="view attendance")

@app.route("/checkattendance")
def checkattendance()->None:
    return render_template("check_attendance.html",pagetitle="check attendance")


if __name__=="__main__":
    app.run(debug=True)