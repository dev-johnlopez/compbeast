from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        print("final send")
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    print("Building email!")
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    print("checking attachments!")
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        print("new email")
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()
        print("new email")

def send_notification_email(player, event, email=None):
    if email == "register":
        send_registration_email(player, event)
    #elif email == "new_event":
    #    send_new_event_email(player, event)
    #elif email == "reminder":
    #    send_registration_reminder_email(player, event)
    #elif email == "leaderboard":
    #    send_leaderboard_email(player, event)
    else:
        return

def send_registration_email(player, event):
    subject = "[Confirmed] You're registered to play!"
    email_name = "team_registration_email"
    #if player.is_confirmed():
    #    email_name = "registration_success_email"
    #else:
    #    email_name = "registration_fail_email"
    with current_app.app_context():
        send_email(subject,
               sender='admin@compbeast.gg',
               recipients=[player.email],
               text_body=render_template('emails/{}.txt'.format(email_name), player=player),
               html_body=render_template('emails/{}.html'.format(email_name), player=player))

def send_new_event_email(player, event):
    subject = "New tournament - compete for your chance to win!"
    email_name = "new_event_email"
    with current_app.app_context():
        send_email(subject,
               sender='admin@compbeast.gg',
               recipients=[player.email],
               text_body=render_template('emails/{}.txt'.format(email_name), player=player),
               html_body=render_template('emails/{}.html'.format(email_name), player=player))

def send_registration_reminder_email(player, event):
    subject = "[Activision Sync] Time is running out!"
    email_name = "registration_reminder_email"
    with current_app.app_context():
        send_email(subject,
               sender='admin@compbeast.gg',
               recipients=[player.email],
               text_body=render_template('emails/{}.txt'.format(email_name), player=player),
               html_body=render_template('emails/{}.html'.format(email_name), player=player))

def send_leaderboard_email(player, event):
    subject = "The leaderboard is available!"
    email_name = "leaderboard_email"
    with current_app.app_context():
        print("Sending leaderboard email to {} for {}!".format(player, event))
        send_email(subject,
               sender='admin@compbeast.gg',
               recipients=[player.email],
               text_body=render_template('emails/{}.txt'.format(email_name), player=player, event=event),
               html_body=render_template('emails/{}.html'.format(email_name), player=player, event=event))
        print("Email sent!")
