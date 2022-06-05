from app import app, db,User,bcrypt,SQLAlchemy,datetime,Faculty,Program,Subject

#Create tables
def create_tables():
    db.create_all()

#Create admin for the app
def create_admin():
    name = "admin"
    email = "admin@pu.edu.np"
    pw_plain = "admin"

    #Encrypted pw
    pw_hash = bcrypt.generate_password_hash(pw_plain).decode('utf-8')
    
    #check if admin with given credentials already exists
    admin = User.query.filter_by(email=email).first()
    if(admin and admin.is_admin):
        print("Admin with given credentials already exists!")
    else:
        admin = User(name, '','','','','',email,pw_hash,True,datetime.utcnow())
        db.session.add(admin)
        db.session.commit()
        #check if admin with given credentials now exists
        admin = User.query.filter_by(email=email).first()
        admin.is_admin = True
        db.session.commit()
        if(admin and admin.is_admin):
            print("Admin with given credentials is created!")


#Populates the tables with least minimum data
def populate_table():
    fac_check = Faculty.query.all()
    if not fac_check:
        faculty = Faculty('Science & Technology')
        db.session.add(faculty)
        db.session.commit()
    pro_check = Program.query.all()
    if not pro_check:
        program = Program('Bachelors in Computer Engineering','Bachelors')
        db.session.add(program)
        db.session.commit()
    subject_check = Subject.query.all()
    if not subject_check:
        sql_entries_bcoe_subjects = sql_entries()
        for row in sql_entries_bcoe_subjects:
            db.session.execute(row)
            db.session.commit()
#Reads sql entries for subjects of bachelors in computer engineering
def sql_entries():
    # Using readline()
    file1 = open('./sql_entries/all-subjects-entries-bcoe.sql', 'r')
    count = 0
    sql_entries = []
    while True:
        count += 1
    
        # Get next line from file
        line = file1.readline()

        #If line is just spaces, then ignore
        if  len(line.strip())>0:
            sql_entries.append(line)
        # end of file is reached
        if not line:
            break
    file1.close()
    return sql_entries

if __name__ == '__main__':
    create_tables()
    create_admin()
    populate_table()