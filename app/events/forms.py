from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, BooleanField, \
                    TextAreaField, SelectField, FieldList, HiddenField
from wtforms.fields.html5 import EmailField, TimeField, DateField, DateTimeField
from wtforms.validators import DataRequired, Optional, Email, Length, ValidationError, InputRequired
from app.events.models import Team, Player, PlayerStat
import datetime
import time

class ConfirmPlayerForm(FlaskForm):
    username = StringField('Confirm Activision Username', validators=[DataRequired()])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(ConfirmPlayerForm, self).__init__(csrf_enabled=csrf_enabled,
                                       *args,
                                       **kwargs)

class PlayerForm(FlaskForm):
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

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(PlayerForm, self).__init__(csrf_enabled=csrf_enabled,
                                       *args,
                                       **kwargs)

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(max=30)])
    start_datetime = DateTimeField('Start Time', format='%m/%d/%Y %I:%M %p', validators=[DataRequired()])
    #start_date = DateField('Start Date', validators=[DataRequired()])
    timezone = SelectField('Timezone', choices=[
                                            ('',	'Select your timezone'),
                                            ('GMT',	'Greenwich Mean Time'),
                                            ('UTC',	'Universal Coordinated Time'),
                                            ('ECT',	'European Central Time'),
                                            ('EET',	'Eastern European Time'),
                                            ('ART',	'Arabic/Egypt Standard Time'),
                                            ('EAT',	'Eastern African Time'),
                                            ('MET',	'Middle East Time'),
                                            ('NET',	'Near East Time'),
                                            ('PLT',	'Pakistan Lahore Time'),
                                            ('IST',	'India Standard Time'),
                                            ('BST',	'Bangladesh Standard Time'),
                                            ('VST',	'Vietnam Standard Time'),
                                            ('CTT',	'China Taiwan Time'),
                                            ('JST',	'Japan Standard Time'),
                                            ('ACT',	'Australia Central Time'),
                                            ('AET',	'Australia Eastern Time'),
                                            ('SST',	'Solomon Standard Time'),
                                            ('NST',	'New Zealand Standard Time'),
                                            ('MIT',	'Midway Islands Time'),
                                            ('HST',	'Hawaii Standard Time'),
                                            ('AST',	'Alaska Standard Time'),
                                            ('PST',	'Pacific Standard Time'),
                                            ('MST',	'Mountain Standard Time'),
                                            ('CST',	'Central Standard Time'),
                                            ('EST',	'Eastern Standard Time'),
                                            ('CNT',	'Canada Newfoundland Time')
                                            ], validators=[DataRequired()])
    players = FieldList(FormField(PlayerForm,
                                  default=lambda:
                                  Player()))

    def __init__(self, event=None, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.event = event

    #def validate(self):
    #    print("*****")
    #    print("***** {}".format(self.start_datetime.data))
    #    return True

    #def validate_start_date(self, field):
    #    print("validating start time")
    #    if self.event is None:
    #        return

    #    if field.data < self.event.start_time.date():
    #        print("ERROR!!!!")
    #        raise ValidationError('The start date must be between {} and {}'.format(self.event.start_time.date(), self.event.end_time.date()))

    #def validate_start_date(self, field):
    #    print("validating start time")
    #    if self.event is None:
    #        return
#
#        if field.data < self.event.start_time.date() or field.data > self.event.end_time.date():
#            print("ERROR!!!!")
#            raise ValidationError('The start date must be between {} and {}'.format(self.event.start_time.date(), self.event.end_time.date()))

    #def validate(self):
    #    rv = FlaskForm.validate(self)
    #    if not rv:
    #        return False

    #    if self.event is None:
    #        return True

    #    start_date_time = datetime.datetime.combine(self.start_date.data,
    #                              self.start_time.data)

    #    if start_date_time < self.event.start_time or start_date_time > self.event.end_time:
    #        self.timezone.errors.append('Event start time (date & time) needs to be between {} and {}'.format(self.event.start_time, self.event.end_time))
    #        return False

    #    return True

class PlayerStatForm(FlaskForm):
    kills = IntegerField("Kills", validators=[InputRequired('This field is required.')])

class MatchForm(FlaskForm):
    placement = IntegerField("Team Placement", validators=[DataRequired()])
    player_stats = FieldList(FormField(PlayerStatForm,
                                  default=lambda:
                                  PlayerStat()))
    external_url = StringField('COD Tracker URL', validators=[DataRequired()])
