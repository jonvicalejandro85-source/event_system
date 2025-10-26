from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Optional
from wtforms.validators import DataRequired, Email 

class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    venue = StringField("Venue", validators=[Optional()])
    start_date = DateField("Start Date", format="%Y-%m-%d", validators=[DataRequired()])
    start_time = TimeField("Start Time", format="%H:%M", validators=[DataRequired()])
    end_date = DateField("End Date", format="%Y-%m-%d", validators=[Optional()])
    end_time = TimeField("End Time", format="%H:%M", validators=[Optional()])
    submit = SubmitField("Save")

class RegisterForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    submit = SubmitField("Register")
