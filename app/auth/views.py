#from app import discord_bp
from app.database import db, PkModel
import flask
from flask import Blueprint, flash, render_template, url_for, current_app, request
from flask_security import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.discord import make_discord_blueprint
from flask_dance.contrib.twitch import make_twitch_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from app.auth.models import OAuth, User, DiscordAccount, TwitchAccount
from app.auth.forms import UserForm

blueprint = Blueprint('users', __name__, url_prefix="/u")

@blueprint.route('/account', methods=['GET', 'POST'])
def account():
    form = UserForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash("Success!")
    return render_template("users/account.html", form=form)

discord_storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
discord_bp = make_discord_blueprint(scope="email", storage=discord_storage)

twitch_bp = make_twitch_blueprint(scope="user_read")
twitch_bp.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)

# create/login local user on successful Discord OAuth login
@oauth_authorized.connect_via(discord_bp)
def discord_logged_in(blueprint, token):
    print("***** CONNECT_VIA")
    if not token:
        flash("Failed to log in with Discord.", category="error")
        return False

    resp = blueprint.session.get('https://discordapp.com/api/users/@me')
    if not resp.ok:
        msg = "Failed to fetch user info from discord."
        flash(msg, category="error")
        return False

    discord_info = resp.json()
    print("Your discord name is {}".format(str(discord_info)))
    print("Your discord name is {}".format(str(discord_info)))
    print("Your discord username is {}".format(str(discord_info['username'])))
    print("Your discord email is {}".format(str(discord_info['email'])))
    #print("****: {}".format(discord.get('/users/@me')))

    discord_info = resp.json()
    discord_user_id = str(discord_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=discord_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=discord_user_id,
            token=token,
        )

    if oauth.user:
        # If this OAuth token already has an associated local account,
        # log in that local user account.
        # Note that if we just created this OAuth token, then it can't
        # have an associated local account yet.
        print("*** Logging in with known users {}".format(oauth.user))
        try:
            login = login_user(oauth.user)
            print("*** Current User Logged In: {}".format(login))
        except:
            print("*** ERROR!!!!")
        flash("Successfully signed in with Discord.")

    else:
        # If this OAuth token doesn't have an associated local account,
        # create a new local user account for this user. We can log
        # in that account as well, while we're at it.
        discord_info_email = discord_info['email']
        discord_info_username = discord_info['username']
        discord_info_discriminator = discord_info['discriminator']
        discord_info_avatar = discord_info['avatar']
        user = None
        try:
            account = DiscordAccount.query.filter_by(username=discord_info_username,discriminator=discord_info_discriminator).one()
            user = account.user
            if user is None:
                referrer = None
                if request.cookies.get('referralID') is not None:
                    referrer = request.cookies.get('referralID')
                user = User(
                    email=discord_info_email,
                    referrer=referrer
                )
                user.add_account(account)
        except NoResultFound:
            account = DiscordAccount(
                email=discord_info_email,
                username=discord_info_username,
                discriminator=discord_info_discriminator,
                avatar=discord_info_avatar,
            )
            user = User.query.filter_by(email=discord_info_email).first()
            if user is None:
                referrer = None
                if request.cookies.get('referralID') is not None:
                    referrer = request.cookies.get('referralID')
                user = User(
                    email=discord_info_email,
                    referrer=referrer
                )
            user.add_account(account)

        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        print("USER: {}".format(user))
        print("OAUTH: {}".format(oauth))
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        print("*** Logging in with unknown user {}".format(user))
        login_user(user)
        flash("Successfully signed in with Discord.")

    # Since we're manually creating the OAuth model in the database,
    # we should return False so that Flask-Dance knows that
    # it doesn't have to do it. If we don't return False, the OAuth token
    # could be saved twice, or Flask-Dance could throw an error when
    # trying to incorrectly save it for us.
    return False

# create/login local user on successful Twitch OAuth login
@oauth_authorized.connect_via(twitch_bp)
def twitch_logged_in(blueprint, token):
    print("***** CONNECT_VIA TWITCH: {}".format(token))
    if not token:
        flash("Failed to log in with Discord.", category="error")
        return False

    resp = blueprint.session.get('https://api.twitch.tv/helix/users')
    print("*** {}".format(resp))
    if not resp.ok:
        msg = "Failed to fetch user info from twitch. Error: {}".format(resp.text)
        flash(msg, category="error")
        return False

    twitch_info = resp.json()['data'][0]
    print("Your discord name is {}".format(str(twitch_info)))
    print("Your discord username is {}".format(str(twitch_info['login'])))
    print("Your discord email is {}".format(str(twitch_info['email'])))
    #print("****: {}".format(discord.get('/users/@me')))

    twitch_user_id = str(twitch_info['id'])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=twitch_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=twitch_user_id,
            token=token,
        )

    if oauth.user is not None and oauth.user != current_user:
        msg = "This account is connected to another account."
        flash(msg, category="error")
        return False

    else:
        # If this OAuth token doesn't have an associated local account,
        # create a new local user account for this user. We can log
        # in that account as well, while we're at it.
        twitch_info_email = twitch_info['email']
        twitch_info_username = twitch_info['login']
        twitch_info_logo = twitch_info['profile_image_url']
        try:
            account = TwitchAccount.query.filter_by(username=twitch_info_username).one()
        except NoResultFound:
            account = TwitchAccount(
                email=twitch_info_email,
                username=twitch_info_username,
                logo=twitch_info_logo
            )
            current_user.add_account(account)

        # Associate the new local user account with the OAuth token
        oauth.user = current_user
        # Save and commit our database models
        db.session.add_all([current_user, oauth])
        db.session.commit()
        # Log in the new local user account
        flash("Successfully signed in with Twitch.")

    # Since we're manually creating the OAuth model in the database,
    # we should return False so that Flask-Dance knows that
    # it doesn't have to do it. If we don't return False, the OAuth token
    # could be saved twice, or Flask-Dance could throw an error when
    # trying to incorrectly save it for us.
    return False
