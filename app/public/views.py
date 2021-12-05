# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    abort,
    request
)
from app.events.models import Event, Team, Player
from app.events.forms import TeamForm, ConfirmPlayerForm
from celery import chain
import stripe
#from app.tasks import new_team_registration_workflow
#from app.events import EventQuery
#from flask_login import login_required, login_user, logout_user
#from compbeast.extensions import login_manager
#from compbeast.public.forms import LoginForm
#from compbeast.user.models import User
#from compbeast.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")

class EventQuery(object):
    @staticmethod
    def get_open_events(limit=None):
        query = Event.query.filter((Event.status == 'Registering') | (Event.status == 'Active')).order_by(Event.start_time)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_highlighted_event():
        return Event.query.filter((Event.status != 'Closed')).order_by(Event.start_time).first()


@blueprint.route("/", methods=["GET", "POST"])
def home():
    events = EventQuery.get_open_events(limit=3)
    quick_register_event = EventQuery.get_highlighted_event()
    print("**** {}".format(quick_register_event.name))
    return render_template("public/index.html", event=quick_register_event, events=events)

@blueprint.route('/<event_id>/register', methods=['GET', 'POST'])
def register(event_id):
    event = Event.query.get_or_404(event_id)
    if event.state != "Registering": abort(404)
    form = TeamForm()
    if form.validate_on_submit():
        team = Team()
        form.populate_obj(team)
        #for player in form.players:
        #    player = Player(name=player.name.data,
        #                    email=player.email.data,
        #                    username=player.username.data)
        #    team.add_player(player)
        event.register_team(team)
        team.save()
        event.save()
        from app.tasks import confirm_player
        [confirm_player.si(player.id, event_id).delay(player_id=player.id, event_id=event_id)
            for player in team.players]
        print("creating stripe endpoint")
        if event.entry_fee > 0:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                  'price_data': {
                    'currency': 'usd',
                    'product_data': {
                      'name': 'Event Entry Fee',
                    },
                    'unit_amount': event.entry_fee * 100,
                  },
                  'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('public.confirm', event_id=event.id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('public.index', _external=True))
            team.payment_id = session['payment_intent']
            team.save()
            print("redirecting to stripe endpoint")
            return redirect(session.url, code=303)

        else:
            team.payment_complete = 1
            team.save()
            return redirect(url_for('public.confirm', event_id=event.id))

    # if we get here, either validation failed or we're just loading the page
    # we can use append_entry to add up to the total number we want, if necessary
    print("**** {}".format(form.errors))
    for i in range(len(form.players.entries), event.team_size):
        form.players.append_entry()

    return render_template("public/register.html", form=form, event=event)

@blueprint.route('/<event_id>/confirm', methods=['GET', 'POST'])
def confirm(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("public/confirm.html", event=event)

@blueprint.route('/<event_id>/cancel', methods=['GET', 'POST'])
def cancel(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("public/confirm.html", event=event)

@blueprint.route('/<player_id>/confirm/p', methods=['GET', 'POST'])
def update_player(player_id):
    form = ConfirmPlayerForm()
    #event = Event.query.get_or_404(1)
    player = Player.query.get_or_404(player_id)
    if form.validate_on_submit():
        player = Player.query.get_or_404(player_id)
        player.username = form.username.data
        player.save()
        player.confirm()
        return redirect(url_for('public.confirm', event_id=player.team.event.id))
    return render_template("public/update_player.html", form=form, event=player.team.event, player=player)

@blueprint.route('/rules', methods=['GET', 'POST'])
def rules():
    return render_template("public/rules.html")

@blueprint.route('/discord', methods=['GET', 'POST'])
def discord():
    return redirect('https://discord.gg/HNTUQUdYKP')

@blueprint.route("/webhooks", methods=["POST"])
def webhooks():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TO BIG')
        return "Payload too large", 400

    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)
    webhook_secret = current_app.config['STRIPE_WEBHOOKSECRET']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, received_sig, webhook_secret
        )
    except ValueError:
        print("Error while decoding event!")
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature!")
        return "Bad signature", 400
    print("***** {}".format(event.type))
    print("***** {}".format(event['type']))
    if event.type == 'charge.succeeded':
        payment_intent = event.data.object
        print(payment_intent)
        team = Team.query.filter_by(payment_id=payment_intent.payment_intent).first()
        team.payment_complete = 1
        #team.payment_status = payment_intent.payment_status
        print("**** {}".format(team))
        team.save()

    print(
        "Received event: id={id}, type={type}".format(
            id=event.id, type=event.type
        )
    )


    return "", 200
