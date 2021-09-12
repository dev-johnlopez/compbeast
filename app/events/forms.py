from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, BooleanField, \
                    TextAreaField, SelectField, FieldList, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Optional, Email, Length
from app.events.models import Team, Player

class ConfirmPlayerForm(FlaskForm):
    username = StringField('Confirm Activision Username', validators=[DataRequired()])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(ConfirmPlayerForm, self).__init__(csrf_enabled=csrf_enabled,
                                       *args,
                                       **kwargs)

class PlayerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=80)])
    username = StringField('Activision Username', validators=[DataRequired(), Length(max=80)])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(PlayerForm, self).__init__(csrf_enabled=csrf_enabled,
                                       *args,
                                       **kwargs)

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(max=30)])
    players = FieldList(FormField(PlayerForm,
                                  default=lambda:
                                  Player()))
