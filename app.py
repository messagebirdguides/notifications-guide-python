from flask import Flask, render_template, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import messagebird

#Configure the app as follows.
app = Flask(__name__)
app.config.from_pyfile('config_file.cfg')

#start MessageBird client
client = messagebird.Client(app.config['SECRET_KEY'])

#set up database and configure app to use database file
project_dir = os.path.dirname(os.path.abspath(__file__)) #gets the project directory
database_file = "sqlite:///{}".format(os.path.join(project_dir, "orderDatabase.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

# Create our database model
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(128))
    items = db.Column(db.String(128))
    status = db.Column(db.String(64))
    def __repr__(self):
        return '<Customer {}>'.format(self.name)

#create all tables and save this change to database
db.create_all()

#in cases of repeated testing, table may already contain data. Clear this table to avoid errors about non-unique primary keys.
db.session.query(Order).delete()

#commit changes to database
db.session.commit()
    
#insert data for orders; using fake data for testing
Order1 = Order(id="c2972b5b4eef349fb1e5cc3e3150a2b6", name="Hannah Hungry", phone="+319876543210", items="1 x Hipster Burger, Fries", status="pending")
Order2 = Order(id="1b992e39dc55f0c79dbe613b3ad02f29", name="Mike Madeater", phone="+319876543211", items="1 x Chef Special Mozzarella Pizza", status="delayed")
Order3 = Order(id="81dc9bdb52d04dc20036dbd8313ed055", name="Don Cheetos", phone="+319876543212", items="1 x Awesome Cheese Platter", status="confirmed")
db.session.add_all([Order1, Order2, Order3])
db.session.commit()

# Page containing table of orders, order update form, and customer notification button.
@app.route('/')
def index():
    #load order data from database
    table = Order.query.all()
    return render_template('index.html', table=table)

#What happens when you submit the order update form
@app.route('/orderUpdate', methods=['POST'])
def update():
    try:
        newStatus = request.form.get("orderStatus")
        currentOrder = Order.query.filter_by(id=request.form.get("id")).first()
        currentOrder.status = newStatus
        db.session.commit()
    except Exception as e:
        flash("Could not update order status")
        flash(e)
    table = Order.query.all()
    return render_template('index.html', table=table)

#What happens when you press the 'notify customer' button
@app.route('/notify', methods=['POST'])
def notify():
    #get data (phone and name) corresponding to customer id in form
    currentOrder = Order.query.filter_by(id=request.form.get("notify_id")).first()
    msgToSend = isOrderConfirmed(currentOrder.status, currentOrder.name)
    try:
        msg = client.message_create('OmNomNom', currentOrder.phone, msgToSend, None)
        flash(currentOrder.name + " was notified that their order is " + currentOrder.status)
    except messagebird.client.ErrorException as e:
        flash("Could not send notification")
        for error in e.errors:
            flash(error.description)
    table = Order.query.all()
    return render_template('index.html', table=table)

def isOrderConfirmed(status, recipientName):
    if status=="pending":
        return "Hello, " + recipientName + ", thanks for ordering at OmNomNom Foods! We're still working on your order. Please be patient with us!"
    elif status=="confirmed":
        return "Hello, " + recipientName + ", thanks for ordering at OmNomNom Foods! We are now preparing your food with love and fresh ingredients and will keep you updated."
    elif status=="delayed":
        return "Hello, " + recipientName + ", sometimes good things take time! Unfortunately your order is slightly delayed but will be delivered as soon as possible."
    elif status=="delivered":
        return "Hello, " + recipientName + ", you can start setting the table! Our driver is on their way with your order! Bon appetit!"
    else:
        return "We can't find your order! Please call our customer support for assistance."

    
#run application
if __name__ == '__main__':
    app.run()
