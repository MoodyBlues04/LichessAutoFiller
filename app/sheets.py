from os import getenv
import pygsheets
from datetime import datetime


class GoogleSheetsApi:
    def __init__(self, sheet_id: str) -> None:
        service_file = getenv('GOOGLE_API_CREDENTIALS_PATH')
        self.__client = pygsheets.authorize(service_file=service_file)
        self.__sheet = self.__client.open_by_key(sheet_id)
        self.__worksheet = None

    def set_worksheet(self, title: str) -> None:
        try:
            self.__worksheet = self.__sheet.worksheet_by_title(title)
        except pygsheets.exceptions.WorksheetNotFound:
            self.__worksheet = self.__sheet.add_worksheet(title, rows=1000)

    def clear_worksheet(self, start: str|tuple) -> None:
        self.__worksheet.clear(start=start)

    def increase_rows_count(self, add_rows: int) -> None:
        self.__worksheet.add_rows(add_rows)

    def get_rows_count(self) -> int:
        return self.__worksheet.rows

    def add_rows(self, rows: list[list]) -> None:
        """ Adds rows at the bottom of existing rows """

        row_idx = self.get_first_empty_row()
        for row in rows:
            self.set_row(row_idx, row)
            row_idx += 1

    def add_to_col(self, col: int, data: list) -> None:
        first_empty_row_idx = self.get_first_empty_row(col)
        self.set_col(col, data, start_row=first_empty_row_idx)

    def set_col(self, col: int, data: list, start_row: int = 2) -> None:
        for idx, el in enumerate(data):
            self.__worksheet.update_value((start_row + idx, col), el)

    def set_row(self, row: int, row_data: list) -> None:
        self.__worksheet.update_row(row, row_data)

    def is_set_row(self, row: int) -> bool:
        row_list = self.get_row(row)
        return len(row_list) > 0

    def get_row(self, row: int, return_as: str = 'cell'):
        return self.__worksheet.get_row(row, return_as, include_tailing_empty=False)

    def get_values(self, start: tuple, end: tuple) -> list:
        return self.__worksheet.get_values(start, end)

    def get_first_empty_row(self, col: int = 1) -> int:
        col_data = self.get_col(col)
        return len(col_data) + 1

    def get_col(self, col: int, return_as: str = 'cell'):
        return self.__worksheet.get_col(col, return_as, include_tailing_empty=False)

    def get_cell(self, row: int, col: int):
        return self.__worksheet.cell((row, col)).value

    def find_in_row(self, target, row: int) -> int|None:
        """ Returns column of found value """
        for idx, el in enumerate(self.get_row(row)):
            if el.value == target:
                return idx + 1
        return None

    def share(self, email_or_domain: str, role: str = 'reader', type: str = 'user') -> None:
        self.__sheet.share(email_or_domain, role=role, type=type)


class GoogleSheetsService:
    __FIO_COL = 4
    __LICHESS_NICK_COL = 7

    def __init__(self, date: datetime):
        self.__api = GoogleSheetsApi(getenv('SPREADSHEET_ID'))
        self.__date = date

    def set_visitings(self, nicks: list[str]) -> None:
        title = self.__get_worksheet_title(visiting_sheet=True)
        self.__api.set_worksheet(title)
        day_col = self.__api.find_in_row(self.__date.strftime('%d.%m'), row=1)
        self.__api.add_to_col(day_col, nicks)

    def get_fio(self, nicks: list[str]) -> list:
        title = self.__get_worksheet_title()
        self.__api.set_worksheet(title)

        fio_list = []
        last_row = self.__api.get_first_empty_row(col=self.__LICHESS_NICK_COL)
        rows = self.__api.get_values((3, self.__FIO_COL), (last_row - 1, self.__LICHESS_NICK_COL))
        
        g_nicks = [row_data[-1].strip() for row_data in rows]
        for nick in nicks:
            if nick not in g_nicks:
                print('Not found:', nick)
        
        for row_data in rows:
            fio = row_data[0]
            lichess_nick = row_data[-1]
            if fio is None or len(fio) == 0:
                continue
            if lichess_nick in nicks:
                fio_list.append(fio)
        return fio_list

    def __get_worksheet_title(self, visiting_sheet: bool = False) -> str:
        day_to_title = {
            0: 'пн/чт',
            1: 'вт/пт',
            2: 'ср/сб',
            3: 'пн/чт',
            4: 'вт/пт',
            5: 'ср/сб',
        }
        return ('Посещения ' if visiting_sheet else '') + day_to_title[self.__date.weekday()]
