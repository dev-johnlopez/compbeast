from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from transitions import Machine

class EventStateMixin(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def status(cls):
        return Column(String())

    @property
    def state(self):
        return self.status

    @state.setter
    def state(self, value):
        if self.status != value:
            self.status = value

    def after_state_change(self):
        db.session.add(self)

    @classmethod
    def init_state_machine(cls, obj, *args, **kwargs):
        states = ['Draft', 'Registering', 'Active', 'Closed']
        #transitions = [
        #    ['open_registration', 'Draft', 'Registering'],
        #    ['activate', 'Registering', 'Active'],
        #    ['close', 'Active', 'Closed']
        #]

        initial = obj.status or states[0]

        machine = Machine(model=obj, states=states, #transitions=transitions,
                          initial=initial,
                          after_state_change='after_state_change')
        machine.add_transition('open_registration', '*', 'Registering')
        machine.add_transition('activate', '*', 'Active', after=obj.close_registration)
        machine.add_transition('close', '*', 'Closed')

        # in case that we need to have machine obj in model obj
        setattr(obj, 'machine', machine)
