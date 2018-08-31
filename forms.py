from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField, SubmitField

#Defines fields in registration and login forms. Includes definitions of validators.

class OrderUpdateForm(FlaskForm):
    status = SelectField('Order status', choices=[('pending', 'Pending'), ('delayed', 'Delayed'), ('confirmed', 'Confirmed'), ('delivered', 'Delivered')])
    customer_id = HiddenField('ID')
    submit = SubmitField('Update')


class NotifyForm(FlaskForm):
    submit = SubmitField('Notify Customer')
