from dotenv import load_dotenv
from os import getenv
from sheets import GoogleSheetsService
from parsers import ItmoAdminParser
from args_parser import make_arg_parser
from lesson_participants_filter import *
from logger import Logger

load_dotenv()


if __name__ == '__main__':
    arg_parser = make_arg_parser()

    args = arg_parser.parse_args()
    week_day = args.date.weekday()

    with open(getenv('ZOOM_NICKS_PATH')) as nicks_file:
        lection_participants = list(map(lambda nick: nick.rstrip(), nicks_file.readlines()))
    
    participation_collector = LessonParticipationCollector(
        args.tournament_id,
        args.required_practice_time,
        args.lection_time,
        lection_participants
    )
    participation_stats = participation_collector.collect_participants_stats()
    
    logger = Logger()
    logger.log_participaton_stats(participation_stats)
    
    good_students_nicks = participation_stats.get_good_students_names()

    google_sheets_service = GoogleSheetsService(logger, args.date)
    fio_list = google_sheets_service.get_fio(good_students_nicks)
    if args.update_sheets:
        google_sheets_service.set_visitings(good_students_nicks)

    if args.fill_visitings:
        arg_parser = ItmoAdminParser(logger, week_day)
        arg_parser.fill_visitings(fio_list)
