from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, BooleanField, \
                    TextAreaField, SelectField, FieldList, HiddenField
from wtforms.fields.html5 import EmailField, TimeField, DateField, DateTimeField
from wtforms.validators import DataRequired, Optional, Email, Length, ValidationError

class UserForm(FlaskForm):
    #name = StringField('Name', validators=[DataRequired(), Length(max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=80)])
    platform = SelectField('Platform', choices=[
                                        ('', 'Account Type'),
                                        ('uno', 'Activision'),
                                        ('psn','PlayStation'),
                                        ('xbl','Xbox'),
                                        ('battle','BattleNet')],
                                      validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
