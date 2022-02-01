from app.database import db, PkModel
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_security import UserMixin, RoleMixin, login_required

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

teams_users = db.Table('teams_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('team_id', db.Integer(), db.ForeignKey('team.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    accounts = db.relationship("ExternalAccount", back_populates="user")
    username = db.Column(db.String(80)) # warzone account info
    platform = db.Column(db.String(80)) # warzone account info
    warzone_player_id = db.Column(db.String(80))
    warzone_avatarUrl = db.Column(db.String(2000))
    warzone_connected = db.Column(db.Boolean, nullable=True)
    teams = db.relationship('Team', secondary=teams_users, backref=db.backref('users', lazy='dynamic'))
    referrer = db.Column(db.String(255))

    def __repr__(self):
        return f"User<{self.email}>"

    def is_admin(self):
        return self.email.lower() == "johnny.lopez617@gmail.com"

    def add_account(self, account):
        if self.accounts is None:
            self.accounts = []
        self.accounts.append(account)

    def get_account_by_type(self, account_type):
        for account in self.accounts:
            if account.type == account_type:
                return account
        return None

    def add_team(self, team):
        if self.teams is None:
            self.teams = []
        self.teams.append(team)

class ExternalAccount(PkModel):
    __tablename__ = 'external_accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="accounts")
    type = db.Column(db.String(50))
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))

    __mapper_args__ = {
        'polymorphic_identity': 'external_accounts',
        'polymorphic_on': 'type'
    }

    def __repr__(self):
        return "{}: {}".format(self.type, self.username)

class DiscordAccount(ExternalAccount):
    __tablename__ = 'discord_account'
    discriminator = db.Column(db.String(255))
    avatar = db.Column(db.String(255))


    __mapper_args__ = {
        'polymorphic_identity': 'discord'
    }

class TwitchAccount(ExternalAccount):
    __tablename__ = 'twitch_account'
    logo = db.Column(db.String(255))


    __mapper_args__ = {
        'polymorphic_identity': 'twitch'
    }


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
