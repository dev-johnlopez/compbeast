from flask import url_for
from app.events.models import Event

def test_public_urls(client, events):
    assert client.get(url_for('public.home')).status_code == 200

    #Event cannot be registered for unless it is in Registering status. app will return 404
    assert client.get(url_for('public.register', event_id=1)).status_code == 404
    #assert client.get(url_for('public.register', event_id=3)).status_code == 404
    #assert client.get(url_for('public.register', event_id=4)).status_code == 404

    #Event registration is available because registration is open
    assert client.get(url_for('public.register', event_id=2)).status_code == 200

    #assert client.get(url_for('public.confirm', event_id=1)).status_code == 200
    #assert client.get(url_for('public.cancel', event_id=1)).status_code == 200
    #assert client.get(url_for('public.update_player', player_id=1)).status_code == 200
    assert client.get(url_for('public.rules')).status_code == 200
