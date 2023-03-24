from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,length,EqualTo
from flask_wtf.file import FileField,FileRequired,FileAllowed

class ContactForm(FlaskForm):
    email = StringField("Your Email:",validators=[Email()])
    message = TextAreaField('Message',validators=[DataRequired(),length(min=10)])
    submit = SubmitField("Submit")