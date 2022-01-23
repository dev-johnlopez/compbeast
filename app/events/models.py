import io
import json
import datetime as dt
from urllib.parse import urlencode, quote_plus
import requests
from datetime import datetime
from app.database import Column, PkModel, db, reference_col, relationship, DateTime
from app.mixins import EventStateMixin
from sqlalchemy import event
from flask import current_app

class Player(PkModel):
    """A role for a user."""

    __tablename__ = "player"
    id = Column(db.Integer, primary_key=True)
    external_id = Column(db.String(80))
    avatarUrl = Column(db.String(2000))
    name = Column(db.String(80))
    email = Column(db.String(255))
    username = Column(db.String(80), nullable=False)
    platform = Column(db.String(80), nullable=True)
    rating = Column(db.Integer)
    kdr = Column(db.Float(asdecimal=True))

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'),
        nullable=True)


    def __init__(self, **kwargs):
        """Create instance."""
        super().__init__(**kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Player({self.email}, {self.username})>"

    def is_confirmed(self):
        print("Player {} is confirmed == {}".format(self.name, self.external_id != None and self.external_id != "" and self.external_id != "None"))
        return self.external_id != None and self.external_id != "" and self.external_id != "None"

    def confirm(self):
        return
        from app.tasks import confirm_player
        confirm_player.si(player.id, player.team.event.id).delay(player_id=player.id, event_id=player.team.event.id)

    def refresh_profile(self):
        try:
            r = requests.get('https://frozen-island-36052.herokuapp.com/player_details?username={}'.format(self.username.replace("#", "%23")))
            print("sent request")
            data = json.loads(r.text)
            print("got data")
            self.external_id = str(data['player'])
            print("got external id - " + self.external_id)
            print(str(data['profile']['lifetime']['mode']['br']['properties']['kdRatio']))
            self.kdr =  data['profile']['lifetime']['mode']['br']['properties']['kdRatio']
            # TODO - Test: player.kdr = int(data['kdr'])
            self.save()
        except:
            print("error!!!! ")
            #app.logger.error('Unhandled exception', exc_info=sys.exc_info())
        finally:
            return

class PlayerStat(PkModel):
    """A role for a user."""

    __tablename__ = "player_statistic"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    kills = db.Column(db.Integer)
    placement = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'),
        nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'),
        nullable=True)


    def __init__(self, **kwargs):
        """Create instance."""
        super().__init__(**kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<PlayerStat({self.match})>"

class Match(PkModel):
    """A role for a user."""

    __tablename__ = "match"
    id = Column(db.Integer, primary_key=True)
    external_id = Column(db.String(80))
    start_time = Column(db.Integer)
    player_stats = relationship("PlayerStat", backref="match", lazy=True)
    placement = Column(db.Integer)
    external_url = Column(db.String(255))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'),
        nullable=True)


    def __init__(self, **kwargs):
        """Create instance."""
        super().__init__(**kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Match({self.team})>"

class Team(PkModel):
    """A role for a user."""

    __tablename__ = "team"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(80))
    players = relationship("Player", backref="team", lazy=True)
    division = Column(db.Integer)
    matches = relationship("Match", backref="team", lazy=True)
    player_stats = relationship("PlayerStat", backref="team", lazy=True)
    payment_id = Column(db.String(255))
    payment_complete = Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'),
        nullable=True)
    manual_score = db.Column(db.Integer)
    start_datetime = Column(db.DateTime, nullable=True)
    timezone = Column(db.String(255))


    def __init__(self, **kwargs):
        """Create instance."""
        super().__init__(**kwargs)

    def __repr__(self):
        return "Team {}, {} Rating".format(self.name, self.rating)

    def is_confirmed(self):
        for player in self.players:
            if not player.is_confirmed():
                return False

        if self.event.prize_pool > 0 and not self.payment_complete:
            return False
        return True

    def refresh_stats(self, event, startTimestamp=None, endTimestamp=None):
        print("** refreshing status")

        from .utils import MatchManager
        print("** getting stats for mode: {}".format(mode))
        stats_manager = MatchManager(team=self, mode=self.mode)
        stats_manager.get_matches()
        self.save()
        #print("**** {}".format(len(matches)))
        #self.matches = stats_manager.get_matches()

        #player = self.players[0]
        #r = requests.get('https://frozen-island-36052.herokuapp.com/stats?username={}'.format(player.username.replace("#", "%23")))
        #data = json.loads(r.text)
        #all_matches = data['matches']
        #for match in all_matches:
        #    player_stats = []
        #    players = match['allPlayers']
        #    for player in players:
        #        if player['mode'] != mode: continue
#
#                player_stat = PlayerStat(username=player['player']['uno'],
#                                        kills=int(player['playerStats']['kills']),
#                                        placement=int(player['playerStats']['teamPlacement']),
#                                        team=self)
#                player_stats.append(player_stat)
#            match = Match(external_id=player['matchID'], player_stats=player_stats, team=self)
#            self.add_match(match)
        #for stat in stats:
        #    player_kills = stat['playerStats']['kills']
        #    team_placement = stat['playerStats']['teamPlacement']
        #io.get_event_loop().run_until_complete(get_team_matches(self))
        #io.run(get_team_matches(self))

    def add_match(self, match):
        if self.matches is None:
            self.matches = []

        print("*** {}***".format(match.external_id))

        if str(match.external_id) is not None and str(match.external_id) != "" and str(match.external_id) != "None":
            if str(match.external_id) in [str(match.external_id) for match in self.matches]:
                print("could not add match {}".format(match.external_id))
                return

        self.matches.append(match)
        print("added match {}".format(match.external_id))

    def add_player(self, player):
        if self.players is None:
            self.players = []
        self.players.append(player)

    @property
    def games_played(self):
        if self.matches is None:
            return 0
        return len(self.matches)

    @property
    def rating(self):
        if self.manual_score is not None and self.manual_score > 0:
            return self.manual_score

        rating = 0
        num_games = 0
        event = self.event
        if event is not None:
            num_games = self.event.num_games
        match_rating = []
        for match in self.matches:
            mRating = 0
            for stat in match.player_stats:
                mRating += stat.kills
            if match.placement == 1:
                mRating += 10
            elif match.placement < 11:
                mRating += 5
            elif match.placement < 26:
                mRating += 2
            match_rating.append(mRating)
        match_rating.sort(reverse=True)
        max_index = len(match_rating) - 1

        if max_index > num_games:
            max_index = num_games
        print("Max Index: {}, Num Games: {}".format(max_index, num_games))
        for i in range(max_index + 1):
            rating += match_rating[i]
        print("Rating: {}".format(rating))
        return rating

    @property
    def placement(self):
        all_ratings = [x.rating for x in self.event.teams]
        all_ratings.sort(key=lambda x: x, reverse=True)
        return all_ratings.index(self.rating) + 1




class Task(PkModel):
    id = Column(db.String(36), primary_key=True)
    name = Column(db.String(128), index=True)
    description = Column(db.String(128))
    event_id = Column(db.Integer, db.ForeignKey('event.id'))
    complete = Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

class Event(PkModel, EventStateMixin):
    """A role for a user."""

    __tablename__ = "event"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(80))
    mode = Column(db.String(50))
    teams = relationship("Team", backref="event", lazy=True)
    tasks = relationship('Task', backref='event', lazy='dynamic')
    teams_per_division = Column(db.Integer)
    num_games = Column(db.Integer, default=1)
    start_time = Column(db.DateTime, nullable=True)
    end_time = Column(db.DateTime, nullable=True)
    prize_pool = Column(db.Integer, default=0)
    entry_fee = Column(db.Integer, default=0)
    flexible_start_ind = Column(db.Boolean, default=0)
    flexible_start_time_length = Column(db.Integer)

    @property
    def team_size(self):
        if self.mode == "br_brsolo": return 1
        elif self.mode == "br_brduos": return 2
        elif self.mode == "br_dbd_dbd": return 2
        elif self.mode == "br_brtrios": return 3
        elif self.mode == "br_brquads": return 4
        return None

    @property
    def playlist(self):
        if self.mode == "br_brsolo": return "Battle Royale"
        elif self.mode == "br_brduos": return "Battle Royale"
        elif self.mode == "br_dbd_dbd": return "Iron Trials"
        elif self.mode == "br_brtrios": return "Battle Royale"
        elif self.mode == "br_brquads": return "Battle Royale"
        return None

    @property
    def num_divisions(self):
        if len(self.teams) == 0:
            return 0
        return sorted(self.teams, key=lambda team: team.division, reverse=True)[0].division

    def get_prize_by_placement(self, placement):
        if placement == 1:
            return self.prize_pool * .50
        elif placement == 2:
            return self.prize_pool * .30
        elif placement == 3:
            return self.prize_pool * .20
        return 0

    def get_teams(self, sort=None):
        if sort == 'leaderboard':
            teams = [team for team in self.teams]
            teams.sort(key=lambda x: x.placement)
            return teams
        return self.teams

    def close_registration(self):
        return
        from app.tasks import generate_leaderboards
        print("generating leaderboard for {}".format(self.id))
        teams = [team for team in self.teams]
        for team in teams:
            if team.is_confirmed():
                for player in team.players:
                    player.refresh_profile()
        generate_leaderboards.delay(event_id=self.id)

    def seed_teams(self):
        print("** launching task")
        self.launch_task("seed_teams", "Seeding teams...")
        print("** launched task")

    def refresh_stats(self):
        for team in self.teams:
            print("{} - {}".format(self.start_time, self.end_time))
            team.refresh_stats(self, self.start_time, self.end_time)
        self.save()
            #match_stats =  get_team_matches(team)
            #for stat in stats:
            #    player_kills = stat['playerStats']['kills']
            #    team_placement = stat['playerStats']['teamPlacement']
            #team.refresh_stats()

    def register_team(self, team):
        if self.teams is None:
            self.teams = []
        if self.status == 'Registering' and len(team.players) == self.team_size:
            self.teams.append(team)

    def can_register(self):
        return self.status == 'Registering'

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    event=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(event=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, event=self,
                                    complete=False).first()

    @property
    def leaderboard(self):
        sorted_teams = sorted(self.teams, key=lambda team: team.rating, reverse=True)
        for team in sorted_teams:
            print("{} - {} Score".format(team, team.rating))
        return sorted_teams


    def __repr__(self):
        return "{}: {} teams are registered".format(self.name, len(self.teams))

event.listen(Event, 'init', Event.init_state_machine)
event.listen(Event, 'load', Event.init_state_machine)
