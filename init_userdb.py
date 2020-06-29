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

    
class user_collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    lastvalue = db.Column(db.String(200), nullable=False, default=1)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

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

inittest1=user_collected_URI(user = "admin", type="plant")
db.session.add(inittest1)
db.session.commit()

inittest2=user_collected_URI(user = "admin", type="plot")
db.session.add(inittest2)
db.session.commit()
        
inittest3=user_collected_URI(user = "admin", type="pot")
db.session.add(inittest3)
db.session.commit()

inittest4=user_collected_URI(user = "admin", type="ear")
db.session.add(inittest4)
db.session.commit()

inittest5=user_collected_URI(user = "admin", type="leaf")
db.session.add(inittest5)
db.session.commit()

inittest6=user_collected_URI(user = "admin", type="sensor")
db.session.add(inittest6)
db.session.commit()

inittest7=user_collected_URI(user = "admin", type="vector")
db.session.add(inittest7)
db.session.commit()

#test

inittest1=user_collected_URI(user = "test", type="plant")
db.session.add(inittest1)
db.session.commit()

inittest2=user_collected_URI(user = "test", type="plot")
db.session.add(inittest2)
db.session.commit()
        
inittest3=user_collected_URI(user = "test", type="pot")
db.session.add(inittest3)
db.session.commit()

inittest4=user_collected_URI(user = "test", type="ear")
db.session.add(inittest4)
db.session.commit()

inittest5=user_collected_URI(user = "test", type="leaf")
db.session.add(inittest5)
db.session.commit()

inittest6=user_collected_URI(user = "test", type="sensor")
db.session.add(inittest6)
db.session.commit()

inittest7=user_collected_URI(user = "test", type="vector")
db.session.add(inittest7)
db.session.commit()

#JE

inittest1=user_collected_URI(user = "jeaneudes", type="plant")
db.session.add(inittest1)
db.session.commit()

inittest2=user_collected_URI(user = "jeaneudes", type="plot")
db.session.add(inittest2)
db.session.commit()
        
inittest3=user_collected_URI(user = "jeaneudes", type="pot")
db.session.add(inittest3)
db.session.commit()

inittest4=user_collected_URI(user = "jeaneudes", type="ear")
db.session.add(inittest4)
db.session.commit()

inittest5=user_collected_URI(user = "jeaneudes", type="leaf")
db.session.add(inittest5)
db.session.commit()

inittest6=user_collected_URI(user = "jeaneudes", type="sensor")
db.session.add(inittest6)
db.session.commit()

inittest7=user_collected_URI(user = "jeaneudes", type="vector")
db.session.add(inittest7)
db.session.commit()
