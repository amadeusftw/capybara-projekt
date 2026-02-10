from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class SubscriptionForm(FlaskForm):
    first_name = StringField('Förnamn', validators=[DataRequired()])
    last_name = StringField('Efternamn', validators=[DataRequired()])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    company = StringField('Företag')
    title = StringField('Titel')
    gdpr = BooleanField('GDPR', validators=[DataRequired()])
    submit = SubmitField('Prenumerera')

from app.presentation.forms import SubscriptionForm