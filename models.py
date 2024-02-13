from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
base_dir = os.path.dirname(__file__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(base_dir,"CRM.db")
db = SQLAlchemy(app)


class Customer(db.Model):
    __tablename__="customers"
    customer_id = db.Column(db.String,primary_key=True)
    customer_name = db.Column(db.String,nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)

    def __init__(self,customer_id,customer_name,age,gender):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.age = age
        self.gender = gender
    
    purchases = db.relationship("Purchase",backref="customers",cascade="delete")

class Purchase(db.Model):
    __tablename__="purchases"
    purchase_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    customer_id = db.Column(db.String,db.ForeignKey("customers.customer_id"))
    date = db.Column(db.DateTime)

    def __init__(self,customer_id,date):
        self.customer_id = customer_id
        self.date = date

    purchase_details = db.relationship("Purchase_detail",backref="purchases",cascade="delete")


class Purchase_detail(db.Model):
    __tablename__="purchase_details"
    purchase_id = db.Column(db.Integer,db.ForeignKey("purchases.purchase_id"),primary_key=True)
    item_id = db.Column(db.String,db.ForeignKey("items.item_id"),primary_key=True)
    quantity = db.Column(db.Integer,nullable=False)

    def __init__(self,purchase_id,item_id,quantity):
        self.purchase_id = purchase_id
        self.item_id = item_id
        self.quantity = quantity


class Item(db.Model):
    __tablename__="items"
    item_id = db.Column(db.String,primary_key=True)
    item_name = db.Column(db.String,nullable=False)
    price = db.Column(db.Integer)

    def __init__(self,item_id,item_name,price):
        self.item_id = item_id
        self.item_name = item_name
        self.price = price

    purchase_details = db.relationship("Purchase_detail",backref="items",cascade="delete")

with app.app_context():
    db.create_all()