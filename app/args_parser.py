from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime


def __valid_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise ArgumentTypeError(f"not a valid date: {s!r}")


def __valid_non_weekend_date(s: str) -> datetime:
    parsed_date = __valid_date(s)
    week_day = parsed_date.weekday()
    if week_day == 6:
        raise Exception('Date cannot be Sunday')
    return parsed_date


def __valid_bool(s: str) -> bool:
    try:
        return bool(int(s))
    except ValueError:
        raise ArgumentTypeError(f"not a valid bool: {s!r} must be 0/1")


def __valid_positive_int(s: str) -> int:
    try:
        parsed_int = int(s)
        if parsed_int < 0: raise ArgumentTypeError(f"not a valid int: {s!r}. Should be >= 0")
        return parsed_int
    except ValueError:
        raise ArgumentTypeError(f"not a valid int: {s!r}")


def make_arg_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        type=__valid_non_weekend_date,
        required=True,
        help="Specify day to fill visitings. format: YYYY-MM-DD"
    )
    parser.add_argument(
        "-t",
        "--tournament_id",
        type=str,
        required=True,
        help="Specify id of tournament to parse visitings from"
    )
    parser.add_argument(
        "-pt",
        "--required_practice_time",
        type=__valid_positive_int,
        required=False,
        default=45,
        help="Enter minimum number of minutes on tournament default=45"
    )
    parser.add_argument(
        "-lt",
        "--lection_time",
        type=__valid_positive_int,
        required=False,
        default=30,
        help="Zoom group lection duration default=30"
    )
    parser.add_argument(
        "-u",
        "--update_sheets",
        type=__valid_bool,
        required=False,
        default=True,
        help="Fill excel sheets or not"
    )
    parser.add_argument(
        "-v",
        "--fill_visitings",
        type=__valid_bool,
        required=False,
        default=True,
        help="Fill myitmo visitings or not"
    )
    return parser