from email.policy import default
from enum import unique
from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager,current_user,login_required,logout_user,login_user,UserMixin

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///tod.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
app.secret_key = 'rajvi7107329'


class Login_info(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column( db.String(200),primary_key=False,unique=False,nullable=False)

class Register_info(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(100),unique=False,nullable=False)
    last_name=db.Column(db.String(100),unique=False,nullable=False)
    gender=db.Column(db.String(10),unique=False,nullable=False)
    register_login_id = db.Column(db.Integer,db.ForeignKey("login_info.id"),nullable=False)
    

class Todo(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200),nullable=True)
    desc=db.Column(db.String(500),nullable=True)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    date_updated=db.Column(db.DateTime,onupdate=datetime.utcnow)
    todo_login_id = db.Column(db.Integer,db.ForeignKey("login_info.id"),nullable=False)


    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return Login_info.query.get(int(id))


@app.route('/login', methods=['POST', 'GET'])
@app.route('/',methods=['POST', 'GET'])
def login():  # put application's code here
    # session.clear()
    if request.method == 'POST':
        user_name = request.form.get('uname')
        password = request.form.get('pwd')
        User=Login_info.query.filter_by(username=user_name,password=password).first()
        if User:
            #lash("Login Succesfull!")
            session['user_id']=User.id
            login_user(User,remember=True)
            return redirect("/home")
            #return render_template('home.html',todo=User)
        else:
            flash("Wrong Username or password!")
            return redirect("/login")
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        gender = request.form.get('myGender')
        user_name = request.form.get('uname')
        password = request.form.get('pwd')
        User=Login_info.query.filter_by(username=user_name).first()
        
        if User:
            flash("Username Already Exsits")
            return redirect('/register')
        else:    
            user=Login_info(username=user_name,password=password)
            db.session.add(user)
            db.session.commit()
            User=Login_info.query.filter_by(username=user_name).first()
            login_user(User,remember=True)
            user=Register_info(first_name=first_name,last_name=last_name,gender=gender,register_login_id=current_user.id)
            db.session.add(user)
            db.session.commit()
            return redirect("/")
    return render_template("register.html")



@app.route("/home",methods=['GET','POST'])
@login_required
def home():
    id=session['user_id']  
    if request.method=='POST':
        title=request.form.get('title')
        desc=request.form.get('desc')
        todo=Todo(title=title,desc=desc,todo_login_id=id)
        db.session.add(todo)
        db.session.commit()
        return redirect('/home')

    print("this is id:",id)
    allToDo=Todo.query.filter_by(todo_login_id=id).all()
    print("info:",allToDo)
    return render_template("home.html",allToDo=allToDo)

@app.route("/delete/<int:sno>")
def delete(sno):
    todo=Todo.query.filter_by(sno=sno).first()
    print(todo)
    db.session.delete(todo)
    db.session.commit()

    return redirect("/home")


@app.route("/update/<int:sno>",methods=['POST','GET'])
def update(sno):
    if request.method=='POST':
        title=request.form.get('title')
        desc=request.form.get('desc')
        todo=Todo.query.filter_by(sno=sno).first()
        todo.title=title
        todo.desc=desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/home")

    todo=Todo.query.filter_by(sno=sno).first()
    return render_template("update.html",todo=todo)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("login.html")
if __name__=="__main__":
    app.run(debug=True)
