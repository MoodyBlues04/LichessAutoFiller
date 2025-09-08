import math

from collections import defaultdict
from lesson_participants_filter import ParticipantsStats


class Logger:
    __MAXIMUM_NICK_LENGTH = 20
    __MILLISECONDS_IN_MINUTE = 60_000
    __BLOCK_DELIMETER = '=' * 20

    def log_participaton_stats(self, participation_stats: ParticipantsStats) -> None:
        self.log_info_block(f"\nPlayers played at least 1 game: {participation_stats.total()}")

        if len(participation_stats.bad_participants) > 0:
            self.log_info_block(f"Players played too few minutes: {len(participation_stats.bad_participants)}")
            for participation in participation_stats.bad_participants:
                print("%s minutes: %s; games: %d; minutes with pauses: %s %s" % (
                    participation.student_name.ljust(self.__MAXIMUM_NICK_LENGTH),
                    self.__format_time(participation.time_played),
                    participation.games_played,
                    self.__format_time(participation.time_with_pauses),
                    "; ZOOM" if participation.lection_attendance else ""
                ))
            print()

        self.log_info_block(f"Players meet criteria: {len(participation_stats.good_participants)}")
        for participation in participation_stats.good_participants:
            print(participation.student_name)
    
    def log_info_block(self, info: str = '') -> None:
        self.log(f"\n{info}\n{self.__BLOCK_DELIMETER}\n")
    
    def log(self, text: str = '') -> None:
        print(text)

    def __format_time(self, time) -> defaultdict:
            doubleTime = (1. * time) / self.__MILLISECONDS_IN_MINUTE
            minutes = math.floor(doubleTime)
            seconds = math.floor((doubleTime - minutes) * 60)
            minutesStr = str(minutes)
            secondsStr = str(seconds)
            if (minutes < 10):
                minutesStr = '0' + minutesStr
            if (seconds < 10):
                secondsStr = '0' + secondsStr
            return minutesStr + ':' + secondsStr
