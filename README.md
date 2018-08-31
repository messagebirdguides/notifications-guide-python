# SMS Order Notifications
### ⏱ 15 min build time 

## Why build SMS order notifications? 

Have you ever ordered home delivery to find yourself wondering whether your order was received correctly and how long it'll take to arrive? Some experiences are seamless and others... not so much. 

For on-demand industries such as food delivery, ridesharing and logistics, excellent customer service during the ordering process is essential. One easy way to stand out from the crowd is providing proactive communication to keep your customers in the loop about the status of their orders. Irresepective of whether your customer is waiting for a package delivery or growing "hangry" (i.e. Hungry + Angry) awaiting their food delivery, sending timely SMS order notifications is a great strategy to create a seamless user experience.

The [MessageBird SMS Messaging API](https://developers.messagebird.com/docs/sms-messaging) provides an easy way to fully automate and integrate a notifications application into your order handling software. Busy employees can trigger the notifications application with the push of a single button - no more confused *hangry* customers and a best-in-class user experience, just like that!

## About our application

In this MessageBird Developer Guide, we'll show you how to build a runnable Order Notifications application in Python. The application is a prototype order management system deployed by our fictitious food delivery company, *Birdie NomNom Foods*.

Birdie NomNom Foods have set up the following workflow:

- New incoming orders are in a _pending_ state.
- Once the kitchen starts preparing an order, it moves to the _confirmed_ state. A message is sent to the customer to inform them about this.
- When the food is ready and handed over to the delivery driver, staff marks the order _delivered_. A message is sent to the customer to let them know it will arrive momentarily.
- If preparation takes longer than expected, it can be moved to a _delayed_ state. A message is sent to the customer asking them to hang on just a little while longer. Thanks to this, Birdie NomNom Foods saves time spent answering *"Where's my order?"* calls.

**Pro-tip:** Follow this tutorial to build the whole application from scratch or, if you want to see it in action right away, you can download, clone or fork the sample application from the MessageBird Developer Guides GitHub repository [UPDATE THIS LINK TO THE PYTHON CODE].

## Getting started

We'll be building our single-page web application with:

* Python 2.7, 
* the [Flask framework](http://flask.pocoo.org/), and
* [MessageBird's REST API package for Python](https://github.com/messagebird/python-rest-api).

### Structure of your application

We'll need the following components for our application to be viable:

- **A data source**: This should be a database or a REST endpoint containing information about our customers and their orders. For this guide, we'll be using a simple SQLite database, since SQLite comes with Python. You can easily modify the sample code to use other SQL databases.
- **A web interface to manage orders**: The web interface will display information on customer orders,  allow us to change the order status, and send SMS messages to customers. We will use the [Flask framework](http://flask.pocoo.org/) to build this web interface.
- **A route handler that contains message sending logic**: This handler will contain logic that:
    1. Checks our order against the orders database.
    2. Updates the database when we update order statuses.
    3. When we click a button, sends an SMS notification to the customer whose order is updated.

### Project Setup

Let's start by creating a folder for your application. In this folder, you can create the following subfolder to contain our Jinja2 template for the webpage:

 - `templates`

#### Packages

We'll use a number of packages from the standard Flask  library, in addition to the [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/) extension. The latter allows us to easily configure database connections and to update or query tables in the database.

Let's install the required Flask packages as follows using the Python package manager `pip`:

````bash
pip install flask
pip install Flask-SQLAlchemy 
````

Next, we also install [MessageBird's REST API package for Python](https://github.com/messagebird/python-rest-api) using `pip`:

````bash
pip install messagebird
````

### Main File

In your application folder, let's create a file named `app.py`. This file will contain most of the application logic. We'll start by importing the packages and modules we need by adding this to the start of the file:

````python
from flask import Flask, render_template, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import messagebird

````

### Create your API Key 🔑

To start making API calls, we need to generate an access key. MessageBird provides keys in _live_ and _test_ modes. For this tutorial you will need to use a live key. Otherwise, you will not be able to test the complete flow. Read more about the difference between test and live API keys [here](https://support.messagebird.com/hc/en-us/articles/360000670709-What-is-the-difference-between-a-live-key-and-a-test-key-).

Go to the [MessageBird Dashboard](https://dashboard.messagebird.com/en/user/index); if you have already created an API key it will be shown right there. Click on the eye icon to make the access key visible, then select and copy it to your clipboard. If you do not see any key on the dashboard or if you're unsure whether this key is in _live_ mode, go to the _Developers_ section and open the [API access (REST) tab](https://dashboard.messagebird.com/en/developers/access). Here, you can create new keys and manage your existing ones.

If you are having any issues creating your API key, please don't hesitate to contact support at support@messagebird.com.

**Pro-tip:** Hardcoding your credentials in the code is a risky practice that should never be used in production applications. For this reason, we will be saving our API key together with other configuration parameters in a separate configuration file, `config_file.cfg`. Another method, also recommended by the [Twelve-Factor App Definition](https://12factor.net/), is to use environment variables. The following is an example of what this configuration file might look like.

````
SECRET_KEY='Put your key here'
DEBUG=True
````
### Load Configuration Variables

After you have imported the appropriate packages and specified your API key, you can initialize the app and load configuration variables from the configuration file. Add the following to `app.py`:

````python
#Configure the app as follows.
app = Flask(__name__)
app.config.from_pyfile('config_file.cfg')
````

## Initialize the MessageBird Client

Now that the application has been configured, we can start the MessageBird client:

````python
#start MessageBird client
client = messagebird.Client(app.config['SECRET_KEY'])
````

## Setting up your data source

We'll use an SQLite database to store our customer data. Flask's SQLAlchemy extension will help us interact with the database.

After initializing the MessageBird client, add the following code to set up the database:

````python
# set up database and configure app to use database file
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

# create all tables and save this change to database
db.create_all()

# Make sure table is already empty before inserting any data.
db.session.query(Order).delete()

#commit changes to database
db.session.commit()
````

We've created a placeholder database in the form of a list of orders, each containing "ID", "Name", "Phone", "Items", and "Status" fields. Next, we insert some sample orders into the table:

````python
Order1 = Order(id="c2972b5b4eef349fb1e5cc3e3150a2b6", name="Hannah Hungry", phone="+14127267380", items="1 x Hipster Burger, Fries", status="pending")
Order2 = Order(id="1b992e39dc55f0c79dbe613b3ad02f29", name="Mike Madeater", phone="+319876543211", items="1 x Chef Special Mozzarella Pizza", status="delayed")
Order3 = Order(id="81dc9bdb52d04dc20036dbd8313ed055", name="Don Cheetos", phone="+319876543212", items="1 x Awesome Cheese Platter", status="confirmed")
db.session.add_all([Order1, Order2, Order3])
db.session.commit()
````

## Dealing with our routes

Now we'll define our routes for displaying order statuses, updating order statuses, and sending notifications.

We'll be using two types of forms in our web application. One type of form lets you select a new order status for an existing order and update the status. The other type lets you send a notification about an order's status to the customer associated with that order.

### Define routes

We'll have the following routes:

- One route displays the table of orders with their respective forms
- The second route handles the POST request for updating an order status
- The third route handles the POST request for notifying the customer of an order status.

In `app.py`, we add the first route as follows:

````python
# Page containing table of orders, order update form, and customer notification button.
@app.route('/')
def index():
    #load order data from database
    table = Order.query.all()
    return render_template('index.html', table=table)
````

### Writing our template

The whole application is going to be on one page, so we can use one Jinja2 template for it.

For `index.html`, write the following code:

````html
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html> <head>
<title></title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
</head>

<body>
<!--If password or username is incorrect, flash error message at top -->
<!--of page-->
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul class=flashes>
    {% for message in messages %}
      <li>{{ message }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
    
  <div class="container">

    <h1>Current Orders</h1>
    <table class="table">
      <thead>
       <th>Name</th>
       <th>Phone</th>
       <th>Items</th>
       <th>Status</th>
       <th>Update status</th>
      </thead>
      <tbody>
      {% for row in table %}
      <tr>
	<td>{{ row.name }}</td>
	<td>{{ row.phone }}</td>
	<td>{{ row.items }}</td>
	<td>{{ row.status }}</td>
	<td><form action="{{ url_for('update') }}" method="post">
	  <input type="hidden" value="{{ row.id }}" name="id">
	  <select name="orderStatus" required>
	    <option value="" selected="selected">--Order status--</option>
	    <option value="pending">Pending</option>
	    <option value="delayed">Delayed</option>
	    <option value="confirmed">Confirmed</option>
	    <option value="delivered">Delivered</option>
	  </select>
	  <input type="submit" value="Update">
	  </form>
	  <form action="{{ url_for('notify') }}" method="post">
	  <input type="hidden" value="{{ row.id }}" name="notify_id">
	  <button type="submit" name="sendMessageTo" value="{{ row.id }}">Notify Customer</button>
	  </form>
	</td>
      </tr>
      {% endfor %}	  
    </tbody></table>

</div>

</body> </html>
````

To improve the display of our table, we've used the popular [Bootstrap] (https://getbootstrap.com/) CSS stylesheet and implemented its `table` [style] (https://getbootstrap.com/docs/4.0/content/tables/) to our table of orders.

The top part of our page displays error messages if any exceptions are encountered when submitting forms. The main part of the page contains a table of orders, as extracted from our SQLite database. Each table row corresponds to one order and displays the customer's name, their phone number, what they ordered, and the current status of the order.

The rightmost column of the table, with the header "Update Status", contains two forms for each row of the table:

- A drop-down menu that lets you submit a change to the status of the order when you select a choice and click "Update". This form contains a hidden field that stores the order ID, which helps us update the correct order upon submission.
- A "Notify Customer" button that sends a message to the customer informing them of the order's current status. This button stores the order ID in its `value` attribute so that our application can quickly look up the phone number for the order.


### Routes for submitting forms

Now, we'll write the routes that let you submit the form for updating an order's status and the form for notifying a customer.

#### `orderUpdate` route

This route processes the POST request from the form to update an order's status. We define it in `app.py` as follows:

````python
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
````

From the form defined in `index.html`, the route obtains the new order status selected in the drop-down menu. It then uses the order ID stored in the form's hidden field to modify the status of the order in the database. If the attempt to obtain the new status and update the old one fails, it flashes the error message at the top of the page, in the region defined in `index.html`.

As a last step, the route also updates the order table to display the new order status. 

#### `notify` route

In our `notify` route, we need to:

1. Get the order ID that we want to send a notification for. This is stored in the hidden field in the second form defined in `index.html`.
2. Get the order status and the phone number associated with that order by looking up the order ID in the database and finding the data corresponding to that order.
3. Send a message to that phone number.

Add the following code to `app.py`:

````python
#What happens when you press the 'Notify Customer' button
@app.route('/notify', methods=['POST'])
def notify():
    #get data (phone and name) corresponding to customer id in form
    currentOrder = Order.query.filter_by(id=request.form.get("notify_id")).first()
    msgToSend = isOrderConfirmed(currentOrder.status, currentOrder.name)
    try:
        msg = client.message_create('OmNomNom', currentOrder.phone, msgToSend, None)
        print msg
        flash(currentOrder.name + " was notified that their order is " + currentOrder.status)
    except messagebird.client.ErrorException as e:
        flash("Could not send notification")
        for error in e.errors:
            print error.description
    table = Order.query.all()
    return render_template('index.html', table=table)
````

We start by parsing our form for the `notify_id` field that contains the order ID for the order of interest. Then we look in our database and find the order that matches `notify_id`. Once we've found the relevant order, we can use its fields to construct a message to send to our customer.

After a message is constructed using the order data, we send a message using the MessageBird Python library's `message_create()` method. If we succeed in doing so, a success message flashes at the top of the page. If the notification fails, an error message is displayed.

We want the route to return the same page that it starts with, so we populate the table with data and use the `index.html` template again.

Notice that in order to construct the notification message, we're calling a `isOrderConfirmed()` helper function to construct our `msgToSend` parameter. Add the code for `isOrderConfirmed()` just under the body of `orderNotify()`:

````python
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
````

Our `isOrderConfirmed()` helper matches the status of the order to a list of predefined messages, and returns a message string (complete with the customer's name). We assign this to the `msgToSend` variable for use when triggering the SMS notification.


## Testing the Application

We now have a fully working application, but we won't be able to test our application without having an order with a real phone number. Plus, if you're using a test API key, our code in `app.py` doesn't give us visible feedback for each `message_create()` call.

To set up a development copy of the code to test if it works, we can modify a few things:

1. Change one of the "Phone" fields in your database table to a test phone number that can receive messages. This phone number should also be saved in your MessageBird account as a contact.
2. Use a live API key when you run the program.

Now, a successful `message_create()` call will result in one of the four messages defined in `isOrderConfirmed()` being sent to the real phone number you used.

You can begin testing your application!

Run your application in the terminal:

````bash
python app.py
````

1. Point your browser at http://localhost:5000/ to see the table of orders.
2. For any order displayed, select a new order status and click "Update" to update the order status. The page should display the updated order status.
3. For any order displayed, click on "Notify Customer" to send an SMS notification to the customer. The phone number associated with that order should receive a message communicating the order status.

## Nice work!

You now have a running SMS Notifications application!

You can now use the flow, code snippets and UI examples from this tutorial as an inspiration to build your own SMS Notifications system. Don't forget to download the code from the MessageBird Developer Guides GitHub repository (ADD LINK HERE WHEN IT EXISTS).

## Next steps

Want to build something similar but not quite sure how to get started? Please feel free to let us know at support@messagebird.com, we'd love to help!
