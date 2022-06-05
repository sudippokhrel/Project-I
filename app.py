import os
from flask import (Flask, Response, request, redirect, jsonify ,config ,flash, send_file,
    render_template, session, url_for, g, Response)
import pymysql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin,login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import  StringField, BooleanField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import check_password_hash,generate_password_hash
import config


app = Flask(__name__)

app.debug = True
app.config.from_object('config')
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config['SECRET_KEY']='1234#ABCD#WXYZ#98765'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class RegistrationForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired(), Length(max=80)])   
    symbol_no = StringField('Symbol No.',validators=[DataRequired(), Length(max=20)])
    registration_no = StringField('Registration No.',validators=[DataRequired(), Length(max=20)])      
    email = StringField('Email',validators=[DataRequired(), Length(max=50)])
    faculty = SelectField('Faculty', choices = [])
    program = SelectField('Program', choices = [])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit  = SubmitField('Register')

    def validate_fields(self,symbol_no, registration_no, email):
        user = User.query.filter_by(symbol_no=symbol_no).first()
        if user:
            flash('Account with provided Symbol No already exits.')

        user = User.query.filter_by(registration_no=registration_no).first()
        if user:
            flash('Account with provided registration No already exits.')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Account with provided email already exits.')
        

    


class LoginForm(FlaskForm):
    symbol_no = StringField('Symbol No.',validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit  = SubmitField('Login')



class ExamForm(FlaskForm):
    semester = IntegerField('Semester',validators=[DataRequired(), Length(max=1)])
    bank_reciept_no = StringField('Bank Reciept No:', validators = [DataRequired()])
    submit  = SubmitField('Submit')



class AdminLoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit  = SubmitField('Login')


class User(db.Model, UserMixin):
    __tablename__ = "User"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    symbol_no = db.Column(db.String(20), nullable=False)
    registration_no = db.Column(db.String(20), nullable=False)
    faculty = db.Column(db.String(50), nullable=False)
    program = db.Column(db.String(50),nullable=False)
    level = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(255),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean,nullable=False)
    date_created= db.Column(db.String(120), default =datetime.utcnow())
   
    def __init__(self, name, symbol_no, registration_no, faculty, program, level,email, password, is_admin,date_created):
        self.name=name
        self.symbol_no=symbol_no
        self.registration_no= registration_no
        self.faculty=faculty
        self.program=program
        self.level=level
        self.password=password
        self.email=email
        self.is_admin = False
        self.date_created=date_created

    # user  = User(register_form.name.data,register_form.symbol_no.data,register_form.registration_no.data,register_form.faculty.data,register_form.program_data,level,hashed_pw,  register_form.email.data,datetime.utcnow())   
    def __repr__(self):
       return f"Name: {self.name}, symbol_no: {self.symbol_no}, reg_no: {self.registration_no}, email: {self.email}"
    
    def get_id(self):
        return (int(self.user_id))

    

class Subject(db.Model):
    __tablename__ = "Subject"
    course_id = db.Column(db.String(20), nullable=False,unique=True,primary_key=True)
    course_name = db.Column(db.String(80), nullable=False)
    course_credits = db.Column(db.Integer, nullable=False)
    course_semester = db.Column(db.Integer,nullable=False)
    def __init__(self, course_id, course_name, course_credits, course_semester):
        self.course_id = course_id
        self.course_name=course_name
        self.course_credits=course_credits
        self.course_semester=course_semester


class Form(db.Model):
    __tablename__ = "Form"
    form_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'),nullable=False)
    semester = db.Column(db.Integer,nullable=False)
    bank_reciept_no = db.Column(db.Integer, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    def __init__(self, user_id, semester, verified, bank_reciept_no):
        self.user_id = user_id
        self.semester = semester
        self.verified = verified
        self.bank_reciept_no = bank_reciept_no

class Faculty(db.Model):
    __tablename__ = "Faculty"
    faculty_id = db.Column(db.Integer, primary_key=True)
    faculty_name = db.Column(db.String(100),nullable=False)

    def __init__ (self,faculty_name):
        self.faculty_name=faculty_name

    def __repr__(self):
        return f"Faculty_id: {self.faculty_id}, Name: {self.faculty_name}"

class Program(db.Model):
    __tablename__ = "Program"
    program_id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.String(100),nullable=False)
    program_level = db.Column(db.String(40), nullable = False)

    def __init__ (self,program_name, program_level):
        self.program_name=program_name
        self.program_level=program_level

    def __repr__(self):
        return f"Program_id: {self.program_id}, Name: {self.program_name}, level: {self.program_level}"



class ReCourses(db.Model):
    __tablename__ = "ReCourses"
    re_courses_id = db.Column(db.Integer, primary_key=True)
    subject1 = db.Column(db.String(100), nullable=True)
    subject2 = db.Column(db.String(100), nullable=True)
    subject3 = db.Column(db.String(100), nullable=True)
    subject4 = db.Column(db.String(100), nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('Form.form_id'),nullable=False)

    
    def __init__(self, re_courses_id, subject1,subject2,subject3,subject4, subject5, form_id):
        self.subject1 = subject1
        self.subject2 = subject2
        self.subject3 = subject3
        self.subject4 = subject4
        self.subject5 = subject5
        self.form_id = form_id

 




#Create all tables in database
#db.create_all()


@app.route('/',methods=['GET'])
def index():
    user_name = ''
    if current_user.is_authenticated:
        user_name = current_user.name
        email = current_user.email
    else:
        return redirect(url_for('login'))
    
    return render_template('index.html' ,name = user_name)

def check_if_admin():
    return current_user.is_admin

@app.route('/login', methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            user = User.query.filter_by(symbol_no=login_form.symbol_no.data).first()
            if user:
                if bcrypt.check_password_hash(user.password,login_form.password.data): #Checking if user exists and also if password matches
                    login_user(user, remember = login_form.remember_me.data) #Login of the user
                    return redirect(url_for('index'))
            flash('Invalid credentials.')
    semi_title= "- Login for Students"
    return render_template('login.html', form= login_form, semi_title=semi_title)


@app.route('/forms', methods=["GET","POST"])
def forms():
    if current_user.is_authenticated:
        if check_if_admin():
            return redirect(url_for('forms_admin'))
        else:
            forms = []
            user = User.query.filter_by(user_id=current_user.user_id).first()
            if user:
                forms = Form.query.filter_by(user_id=current_user.user_id).all()
            semi_title= "- Forms for Students"
            return render_template('forms.html',forms_result = forms, semi_title= semi_title)
    
    return redirect(url_for('login'))


@app.route('/view', methods=["GET"])
@login_required
def view_form():
    form_id = request.args.get("form_id")
    if form_id:
        form = Form.query.filter_by(form_id=form_id).first()
        if (not form) or (form.verified==False):
            return redirect(url_for('forms'))
        
        user = User.query.filter_by(user_id = current_user.user_id).first()
        semester = form.semester
        subs = Subject.query.filter_by(course_semester=semester).all()
        return render_template('view.html',user=user,form=form,subs=subs)
    return redirect(url_for('forms'))




@app.route('/verify', methods=["GET"])
@login_required
def verify():
    if current_user.is_authenticated and check_if_admin():
        form_id = request.args.get("form_id")
        if form_id:
           if (Form.query.filter_by(form_id= form_id).first()):
               form = Form.query.get(form_id)
               form.verified = True
               db.session.commit()
    return redirect(url_for('forms'))


@app.route('/aboutus', methods=["GET"])
def about_us():
   return render_template('aboutus.html')




@app.route('/new_form', methods=["GET","POST"])
def new_form():
    if current_user.is_authenticated:
        form = ExamForm()
        if request.method == 'POST':
            semester = form.semester.data
            bank_reciept_no = form.bank_reciept_no.data
            if (semester > 0 and semester <9) and bank_reciept_no:
                exam_form = Form(current_user.user_id,semester,False,bank_reciept_no)
                db.session.add(exam_form)
                db.session.commit()
                flash('Form Added successfully.')
                return redirect(url_for('forms'))
            flash('Invalid Data Provided')
                
            
        return render_template('newform.html',semi_title="New Form", form=form)
    return redirect(url_for('login'))


@app.route('/formsadmin', methods=["GET","POST"])
@login_required
def forms_admin():
    if current_user.is_authenticated:
        if check_if_admin():
            all_forms = Form.query.all()
            return render_template("formsadmin.html", forms_result=all_forms)
        else:
            return redirect(url_for('forms'))
    return redirect(url_for('login'))
        

#Todo: fix admin login
@app.route('/adminlogin', methods=["GET","POST"])
def admin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = AdminLoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            admin = User.query.filter_by(email=login_form.email.data).first()
            if admin:
                if bcrypt.check_password_hash(admin.password,login_form.password.data) and admin.is_admin: #Checking if user exists and also if password matches
                    login_user(admin, remember = login_form.remember_me.data) #Login of the user
                    return redirect(url_for('index'))

            flash('Invalid credentials.')
    semi_title= "- Login for Admins"
    return render_template('loginadmin.html', form= login_form, semi_title=semi_title)

@app.route('/register', methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    faculty= Faculty.query.all() #faculty 
    program = Program.query.all() #program 
    faculty_choices  = []
    program_choices  = []
    
    for x in faculty: faculty_choices.append(x.faculty_name)
    for x in program: program_choices.append(x.program_name)
    
    
    register_form = RegistrationForm()
    register_form.faculty.choices = faculty_choices
    register_form.program.choices = program_choices
    
    if request.method == 'POST':
        if register_form.validate_on_submit():
            if(register_form.password.data == register_form.confirm_password.data):
            
                hashed_pw = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
                name = register_form.name.data
                symbol_no = register_form.symbol_no.data
                reg_no = register_form.registration_no.data
                email = register_form.email.data
                program = register_form.program.data
                faculty = register_form.faculty.data

                selected_program = Program.query.filter_by(program_name=register_form.program.data).first() #Get details about selected program
                level = selected_program.program_level #Level of selected program

                #User object with all necessary data to be added into db
                user  = User(name,symbol_no,reg_no,faculty,program,level,email,hashed_pw,False,datetime.utcnow())
                db.session.add(user)
                db.session.commit()
                flash(f'Registration successfull. Please login to continue.')
                return redirect(url_for('login'))
    semi_title= "- Login for Students"
    return render_template('register.html', form=register_form, semi_title= semi_title)


#Endpoint for log out
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True,threaded=true)




