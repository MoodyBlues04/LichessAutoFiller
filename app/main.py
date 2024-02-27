from dotenv import load_dotenv
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from os import getenv
from app.sheets import GoogleSheetsService
from parsers import ItmoAdminParser

load_dotenv()


def valid_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise ArgumentTypeError(f"not a valid date: {s!r}")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        type=valid_date,
        required=True,
        help="Specify day to fill in. format: YYYY-MM-DD"
    )

    args = parser.parse_args()
    week_day = args.date.weekday()
    if week_day == 6: raise Exception('Date cannot be Sunday')

    # TODO retrieve nicks from lichess API

    with open(getenv('LICHESS_NICKS_PATH')) as nicks_file:
        nicks = list(map(lambda nick: nick.rstrip(), nicks_file.readlines()))

    google_sheets_service = GoogleSheetsService(args.date)
    # google_sheets_service.set_visitings(nicks)
    fio_list = google_sheets_service.get_fio(nicks)
    
    print('Students on lesson:', len(nicks), len(fio_list))

    # parser = ItmoAdminParser(week_day)
    # parser.fill_visitings(fio_list)



