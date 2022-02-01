from app.events.models import Event

class EventQuery(object):
    @staticmethod
    def get_open_events(limit=None, start_time=None, end_time=None):
        query = Event.query.filter((Event.status == 'Registering') | (Event.status == 'Active')).order_by(Event.start_time)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_registerable_events(limit=None, start_time=None, end_start_time=None):
        query = Event.query.filter(Event.status == 'Registering').order_by(Event.start_time)
        if start_time is not None:
            query = query.filter(Event.start_time >= start_time)
        if end_start_time is not None:
            query = query.filter(Event.start_time <= end_start_time)
        if limit is not None:
            query = query.limit(limit)
        return query.all()
