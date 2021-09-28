import requests
import json
from app.events.models import PlayerStat, Match
from datetime import timezone

class MatchManager():

    def __init__(self, team, mode):
        self.team = team
        self.mode = mode

    def get_matches(self):
        print("** getting matches")
        matches = []
        possible_matches = self.get_possible_matches_from_activision()
        print("** pre-filter")
        if possible_matches is None:
            return
        filtered_matches = self.filter_possible_matches(possible_matches)
        for match in filtered_matches:
            self.team.add_match(self.adapt_match(match))

    def filter_possible_matches(self, possible_matches):
        matches = []
        player_ids = [player.external_id for player in self.team.players if player.external_id is not None]
        for match in possible_matches:
            #print(match['allPlayers'][0]['mode'])
            if match['allPlayers'][0]['mode'] != self.mode:
                #print("invalid mode")
                continue

            all_players = match['allPlayers']
            possible_players = []
            team_names = []
            for player in all_players:
                #print(player)
                player_info = player['player']
                username = player_info['username']
                player_id = player_info['uno']
                team_name = player_info['team']
                #print("{} in {}: {}".format(player_id, player_ids, player_id in player_ids))
                for id in player_ids:
                    print(id)
                    print(player_id)
                    if int(id) - int(player_id) == 0:
                        #print("testing...")
                        possible_players.append(player)
                        team_names.append(team_name)
                        break

            valid_players = []
            valid_player_stats = []
            for team_name in team_names:
                valid_player_count = 0
                valid_matches = []
                for player in possible_players:
                    if player['player']['team'] == team_name:
                        valid_players.append(player)
                if len(valid_players) == len(self.team.players):
                    #print(json.dumps(valid_players, indent=10))

                    valid_player_stats = valid_players
                    break

            if len(valid_player_stats) == len(self.team.players):
                matches.append({
                    "id": match['allPlayers'][0]['matchID'],
                    "utcStartSeconds": match['allPlayers'][0]['utcStartSeconds'],
                    "stats": valid_player_stats
                })
        return matches

    def get_possible_matches_from_activision(self):
        print("** getting matches from activision")
        try:
            if self.team.players is None or len(self.team.players) == 0:
                # TODO:  - throw exception
                return
            player = self.team.players[0]
            url = 'https://frozen-island-36052.herokuapp.com/stats?username={}'.format(player.username.replace("#", "%23"))
            url += '&start={}'.format(self.get_start_time(self.team))
            url += '&end={}'.format(self.get_end_time(self.team))
            print("** GETTING URL: {}".format(url))
            r = requests.get(url)
            #print(r.text)
            data = json.loads(r.text)
            all_matches = data['matches']
        except:
            print('error getting status for team: {} - player: {}'.format(self.team, self.team.players[0]))
            return None
        return all_matches

    def adapt_match(self, match):
        player_stats = []
        for stat in match['stats']:
            player_stat = PlayerStat(username=stat['player']['uno'],
                                    kills=int(stat['playerStats']['kills']),
                                    placement=int(stat['playerStats']['teamPlacement']))
            player_stats.append(player_stat)
        match = Match(external_id=str(match['id']), player_stats=player_stats, start_time=int(match['utcStartSeconds']))
        return match

    def get_start_time(self, team):
        if team.matches is None or len(team.matches) == 0:
            return to_timestamp(team.event.start_time)
        else:
            sorted_matches = sorted(team.matches, key=lambda match: match.start_time, reverse=True)
            recent_start_time = sorted_matches[0].start_time
            if recent_start_time is None: return to_timestamp(team.event.start_time)
            else:
                print(recent_start_time)
                return recent_start_time #match is already in correct format. Don't need to convert to timestamp

    def get_end_time(self, team):
        return 0#to_timestamp(self.team.event.end_time)



def to_timestamp(datetime):
    return int(datetime.replace(tzinfo=timezone.utc).timestamp()) * 1000

def get_sorted_leaderboard(teams):
    if len(teams) == 0:
        return []
    elif len(teams) == 1:
        return teams

    teams.sort(key=lambda: team: team.rating, reverse=True)

    leaderboard = []
    team_placements = []
    current_rating = teams[0].rating

    for team in teams:
        if team.rating != current_rating:
            leaderboard.append(team_placements)
            team_placements = []
            current_rating = team.rating
        team_placements.append(team)

    return leaderboard
