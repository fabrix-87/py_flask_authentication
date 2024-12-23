from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user, AnonymousUserMixin
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# CREATE TABLE IN DB


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

with app.app_context():
    db.create_all()    


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not isinstance(current_user, AnonymousUserMixin):
        return redirect(url_for('home'))
    
    if (request.method == 'POST'):
        new_user = User (
            name = request.form['name'],
            email = request.form['email'],
            password = generate_password_hash(request.form['password'],'pbkdf2:sha256',8)
        )
        
        result = db.session.execute(db.select(User).where(User.email == new_user.email))
        user = result.scalar()
        
        # if user already exist, go to login page
        if user != None:
            flash('You are already registered with this email','error')        
            return redirect(url_for('login')) 
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)   
        
        return redirect(url_for('secrets'))
    else:
        return render_template("register.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if not isinstance(current_user, AnonymousUserMixin):
        return redirect(url_for('home'))
    
    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        
        if user == None:
            flash('No user found','error')
        
        elif check_password_hash(user.password, password):                  
            login_user(user)            
            return redirect(url_for('secrets'))
        else:
            flash('Wrong password','error')
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    pass


if __name__ == "__main__":
    app.run(debug=False)
