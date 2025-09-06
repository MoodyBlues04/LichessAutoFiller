import ndjson
import requests

from typing import Callable
from collections import defaultdict


# todo refactor
class TournamentGameStatsCollector:
    def __init__(self, games: list) -> None:
        self.__games = games

    def count_games_played(self) -> defaultdict:
        return self.__reduce_players_stats(lambda old, _: old + 1)

    def count_time_played_in_msec(self) -> defaultdict:
        return self.__reduce_players_stats(
            lambda old, game: old + game['lastMoveAt'] - game['createdAt']
        )

    def get_first_game_start(self) -> defaultdict:
        return self.__reduce_players_stats(
            lambda old, game: game['createdAt'] if old == 0 else min(old, game['createdAt'])
        )

    def get_last_game_end(self) -> defaultdict:
        return self.__reduce_players_stats(lambda old, game: max(old, game['lastMoveAt']))
    
    def __reduce_players_stats(self, reducer: Callable) -> defaultdict:
        result = defaultdict(int)
        for game in self.__games:
            for color in 'white', 'black':
                player = game['players'][color]['user']['name']
                result[player] = reducer(result[player], game)
        return result


class Participant:
    def __init__(self, student_name: str, time_played: int, time_with_pauses: int, games_played: int, lection_attendance: bool = False) -> None:
        self.student_name = student_name
        self.time_played = time_played
        self.time_with_pauses = time_with_pauses
        self.games_played = games_played
        self.lection_attendance = lection_attendance


class ParticipantsStats:
    def __init__(self, good_participants: list[Participant] = [], bad_participants: list[Participant] = []) -> None:
        self.good_participants = good_participants
        self.bad_participants = bad_participants
    
    def sort_stats(self) -> None:
        self.bad_participants.sort(key=lambda participant: participant.time_played, reverse=True)
        self.good_participants.sort()
    
    def total(self) -> int:
        return len(self.good_participants) + len(self.bad_participants)


class LessonParticipationCollector:
    __MILLISECONDS_IN_MINUTE = 60_000

    def __init__(
        self,
        tournament_id: str,
        required_practice_time: int,
        lection_time: int,
        lection_participants: list[str]
    ) -> None:
        self.__tournament_id = tournament_id
        self.__required_practice_time = required_practice_time
        self.__lection_time = lection_time
        self.__lection_participants = lection_participants


    def collect_participants_stats(self) -> ParticipantsStats:
        """
        Returns list of participants who met time criteria
        """
        
        tournament_games = self.__get_tournament_games()
        stats_collector = TournamentGameStatsCollector(tournament_games)
        
        games_played = stats_collector.count_games_played()
        time_played = stats_collector.count_time_played_in_msec()
        time_played = self.__add_lection_participation_time(time_played)
        first_game_starts = stats_collector.get_first_game_start()
        last_game_end = stats_collector.get_last_game_end()

        participants_stats = ParticipantsStats()

        for student_name in time_played.keys():
            participant = Participant(
                student_name,
                time_played[student_name],
                last_game_end[student_name] - first_game_starts[student_name],
                games_played[student_name],
                self.__is_worked_in_zoom(student_name)
            )
            if participant.time_played < self.__required_practice_time * self.__MILLISECONDS_IN_MINUTE:
                participants_stats.bad_participants.append(participant)
            else:
                participants_stats.good_participants.append(participant)
        
        return participants_stats
       
    # todo retrieve http-client class 
    def __get_tournament_games(self) -> list:
        return requests.get(
            f"https://lichess.org/api/tournament/{self.__tournament_id}/games",
            headers={'Accept': 'application/x-ndjson'},
            params={'tags': 'false'}
        ).json(cls=ndjson.Decoder)

    def __add_lection_participation_time(self, time_played: defaultdict) -> defaultdict:
        for student_name in self.__lection_participants:
            time_played[student_name] = time_played.get(student_name, 0)

        for student_name in time_played.keys():
            if self.__is_worked_in_zoom(student_name):
                time_played[student_name] += self.__lection_time * self.__MILLISECONDS_IN_MINUTE
        
        return time_played

    def __is_worked_in_zoom(self, student_name) -> bool:
        return self.__lection_participants.count(student_name) > 0
