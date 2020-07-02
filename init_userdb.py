#init_userdb.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.secret_key = b'52d8851b5d6cbe74f7c8bb01974008140b0ae997e5b2efd987ed5b90'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_design.db'
db = SQLAlchemy(app)
########################################################################
class custom_design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return "Design %r" %self.id

class collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "URI %r" %self.id
    
class user_collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    lastvalue = db.Column(db.String(200), nullable=False, default=1)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class collected_variables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    URI = db.Column(db.String(200), nullable=False)
    Entity = db.Column(db.String(50), nullable=False)
    Quality = db.Column(db.String(50), nullable=False)
    Method = db.Column(db.String(50), nullable=False)
    Unit = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "Variable %r" %self.id

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    # password = db.Column(db.String)
    password_hash =db.Column(db.String)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

db.create_all()
usertest = User(username = "test")
usertest.set_password("test")
db.session.add(usertest)
useradmin = User(username="admin")
useradmin.set_password("admin")
db.session.add(useradmin)
user_je = User(username="jeaneudes")
user_je.set_password("pic3.14")
db.session.add(user_je)
db.session.commit()

inittest0=user_collected_URI(user = "admin", type="actuator")
db.session.add(inittest0)
inittest1=user_collected_URI(user = "admin", type="plant")
db.session.add(inittest1)
inittest2=user_collected_URI(user = "admin", type="plot")
db.session.add(inittest2)
inittest3=user_collected_URI(user = "admin", type="pot")
db.session.add(inittest3)
inittest4=user_collected_URI(user = "admin", type="ear")
db.session.add(inittest4)
inittest5=user_collected_URI(user = "admin", type="leaf")
db.session.add(inittest5)
inittest6=user_collected_URI(user = "admin", type="sensor")
db.session.add(inittest6)
inittest7=user_collected_URI(user = "admin", type="vector")
db.session.add(inittest7)
#test
inittest0=user_collected_URI(user = "test", type="actuator")
db.session.add(inittest0)
inittest1=user_collected_URI(user = "test", type="plant")
db.session.add(inittest1)
inittest2=user_collected_URI(user = "test", type="plot")
db.session.add(inittest2)
inittest3=user_collected_URI(user = "test", type="pot")
db.session.add(inittest3)
inittest4=user_collected_URI(user = "test", type="ear")
db.session.add(inittest4)
inittest5=user_collected_URI(user = "test", type="leaf")
db.session.add(inittest5)
inittest6=user_collected_URI(user = "test", type="sensor")
db.session.add(inittest6)
inittest7=user_collected_URI(user = "test", type="vector")
db.session.add(inittest7)
#JE
inittest0=user_collected_URI(user = "jeaneudes", type="actuator")
db.session.add(inittest0)
inittest1=user_collected_URI(user = "jeaneudes", type="plant")
db.session.add(inittest1)
inittest2=user_collected_URI(user = "jeaneudes", type="plot")
db.session.add(inittest2)
inittest3=user_collected_URI(user = "jeaneudes", type="pot")
db.session.add(inittest3)
inittest4=user_collected_URI(user = "jeaneudes", type="ear")
db.session.add(inittest4)
inittest5=user_collected_URI(user = "jeaneudes", type="leaf")
db.session.add(inittest5)
inittest6=user_collected_URI(user = "jeaneudes", type="sensor")
db.session.add(inittest6)
inittest7=user_collected_URI(user = "jeaneudes", type="vector")
db.session.add(inittest7)
db.session.commit()
