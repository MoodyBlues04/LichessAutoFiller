from dotenv import load_dotenv
from os import getenv
from app.sheets import GoogleSheetsService
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
    
    Logger().log_participaton_stats(participation_stats)
    
    visitings = map(lambda participant: participant.student_name, participation_stats.good_participants)

    google_sheets_service = GoogleSheetsService(args.date)
    if args.update_sheets:
        google_sheets_service.set_visitings(visitings)
    fio_list = google_sheets_service.get_fio(visitings)

    print(f'Students on lesson. zoom file: {len(visitings)}, parsed: {len(fio_list)}')

    if args.fill_visitings:
        arg_parser = ItmoAdminParser(week_day)
        arg_parser.fill_visitings(fio_list)
