from __future__ import annotations

import datetime
import email
import imaplib
import logging
import os.path
import tempfile
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from os import listdir
from os.path import isfile, join

import pikepdf as pdf
import pandas as pd
import tabula
from typing import List
import re

from billy_data.category import Category, CategoryService
from billy_data.repo import DataRepo, data_repo
from billy_data import LOGGER


@dataclass
class DataPaths:
    root: str
    raw: str
    no_pass: str
    tables: str
    data: str
    all_data: str

    def get_path_from_base_name_or_abs_path(self, data_path: str, file_name: str) -> str:
        base_name = os.path.basename(file_name)
        return os.path.join(data_path, base_name)

    def raw_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.raw, file_name)

    def no_pass_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.no_pass, file_name)

    def tables_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.tables, file_name)

    def data_file(self, file_name: str) -> str:
        return self.get_path_from_base_name_or_abs_path(self.data, file_name)

    def dirs(self):
        return [v for k, v in self.__dict__.items() if k != 'all_data']


def data_paths(data_repo: DataRepo) -> DataPaths:
    return DataPaths(
        root=data_repo.abs_path('bank_statements'),
        raw=data_repo.abs_path('bank_statements', 'raw'),
        no_pass=data_repo.abs_path('bank_statements', 'no_pass'),
        tables=data_repo.abs_path('bank_statements', 'tables'),
        data=data_repo.abs_path('bank_statements', 'data'),
        all_data=data_repo.abs_path('bank_statements', 'data.json'),
    )


def create_data_paths() -> list[str]:
    repo = data_repo
    paths = data_paths(repo).dirs()
    return repo.create_if_not_exists(*paths)


class ImapClient:
    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.mail = imaplib.IMAP4_SSL(host, port)

    def login(self):
        self.mail.login(self.user, self.password)

    def select(self, mailbox: str):
        status, data = self.mail.select(mailbox)
        if status != "OK":
            raise Exception(status)
        return status, data

    def search(self, criteria: str):
        status, data = self.mail.search(None, criteria)
        if status != "OK":
            raise Exception(status)
        return status, data

    def fetch(self, mail_id: str):
        status, data = self.mail.fetch(mail_id, '(RFC822)')
        if status != "OK":
            raise Exception(status)
        return data

    def close(self):
        self.mail.close()
        self.mail.logout()

    def __enter__(self):
        self.login()
        LOGGER.debug(f'IMAP login.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        LOGGER.debug(f'IMAP close and logout.')


class SearchCriteria:
    def __init__(self):
        self.all_subjects = ['Extras de cont Banca Transilvania', 'Extras de cont Star Gold']

    def since(self, date: str):
        return f"SINCE {date}"

    def on_date(self, date: str):
        return f"ON {date}"

    def all(self):
        return self.subject(self.all_subjects)

    def subject(self, subject_list: List[str]) -> str:
        _criteria = " ".join([f'"{subject}"' for subject in subject_list])
        _one = f'SUBJECT {_criteria}'
        _list = f'OR SUBJECT {_criteria}'
        return _one if len(subject_list) == 1 else _list

    @staticmethod
    def all_data():
        return SearchCriteria().all()


def bank_statement(df: pd.DataFrame):
    bank_statement_info = BankStatementInfo.from_raw_data(df)
    return BankStatementData(df,
                             bank_statement_info) if bank_statement_info.statement_type == BankStatementType.GENERATED else BankStatementDataRequested(
        df, bank_statement_info)


class BankStatementService:
    def __init__(self, user, password, host, port, card_statement_pdf_password):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.mail = ImapClient(user, password, host, port)
        self.search_criteria = SearchCriteria()
        self.data_repo = data_repo
        self.card_statement_pdf_password = card_statement_pdf_password
        self.paths = data_paths(self.data_repo)
        self.categories = CategoryService().get_all()

    def _search_card_statements(self, mail: ImapClient, search_criteria: str) -> List[bytes]:
        mail.select("Inbox")
        LOGGER.debug(f'Search criteria: {search_criteria}')
        status, data = mail.search(search_criteria)
        mail_ids = data[0]
        LOGGER.debug(f'Card statements mail ids: {mail_ids}')
        return mail_ids.split()

    def download_attachment(self, mail_id: str, email_message) -> str:
        downloaded_file = None
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            file_name = part.get_filename()
            # some mails contain images
            if bool(file_name) and file_name.endswith('.pdf'):
                destination_file = self.paths.raw_file(f'bank_statement_{mail_id}.pdf')
                downloaded_file = self.data_repo.save(destination_file, part.get_payload(decode=True))
                LOGGER.info(f'Downloaded "{file_name}" from email with id {mail_id} at path {downloaded_file}.')
        return downloaded_file

    def collect(self, search_criteria: str = SearchCriteria.all_data()) -> List[str]:
        downloaded_files = []
        with self.mail:
            mail_ids = self._search_card_statements(self.mail, search_criteria=search_criteria)
            for mail_id in mail_ids:
                _mail_id = mail_id.decode('utf-8')
                data = self.mail.fetch(_mail_id)
                raw_email = data[0][1]
                raw_email_string = raw_email.decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                downloaded_files.append(self.download_attachment(_mail_id, email_message))
        return downloaded_files

    def save_with_no_password(self, from_file: str):
        bytes_stream = data_repo.read_stream(from_file)
        file = pdf.open(bytes_stream, password=self.card_statement_pdf_password)
        destination_file = self.paths.no_pass_file(from_file)
        LOGGER.debug(f'Saved pdf without password: {destination_file}')
        write_bytes_stream = BytesIO()
        file.save(write_bytes_stream)
        write_bytes_stream.seek(0)
        data_repo.save(file_name=destination_file, data=write_bytes_stream)
        return destination_file

    def transform(self, from_file) -> dict:
        file_no_pass = self.save_with_no_password(from_file)
        file_tables = self.extract_tables(file_no_pass)
        return {
            'file_no_pass': file_no_pass,
            'file_tables': file_tables,
            'file_data': self.extract_data(file_tables)
        }

    def find_category(self, desc):
        _desc = desc
        _category = 'other'
        for category in self.categories:
            if any([key_word in _desc.lower() for key_word in category.key_words]):
                _category = category.name
        return _category

    def load(self, files: list[str]) -> dict:
        destination_file = self.paths.all_data
        dfs = []
        existing_data_df = None
        if len(files) == 1 and files[0] == 'ALL':
            dfs = []
            files = self.data_repo.list_files(self.paths.data)
        else:
            if data_repo.exists(destination_file):
                existing_data_df = pd.read_json(self.data_repo.get(destination_file))
                # dfs.append(existing_data_df)
        LOGGER.info(f'Loading files...')
        LOGGER.info(files)
        for file_name in files:
            df = pd.read_json(self.data_repo.get(self.paths.data_file(file_name)))
            dfs.append(df)
        dfs_to_concat = [existing_data_df, *dfs] if existing_data_df is not None else dfs
        df_all = pd.concat(dfs_to_concat, ignore_index=True)
        df_all['category'] = df_all['desc'].apply(lambda desc: self.find_category(desc))
        df_all = df_all.drop_duplicates(subset=['category', 'date', 'suma'], ignore_index=True)
        self.data_repo.save(destination_file, bytes(df_all.to_json().encode('utf-8')))
        return {
            'data_file': destination_file,
            'df_no': len(dfs),
            'total_bank_statements_entries': len(df_all)
        }

    def extract_tables(self, from_file):
        destination_file = self.paths.tables_file(from_file.replace('.pdf', '.csv'))
        with tempfile.NamedTemporaryFile() as input_file:
            with tempfile.NamedTemporaryFile() as output_file:
                # print(input_file.name)
                input_file.write(data_repo.read(file_name=from_file))
                input_file.seek(0)
                # area = self.get_area()
                tabula.convert_into(input_file.name, output_file.name, output_format="csv", pages='all', stream=True,
                                    guess=False)
                output_file.seek(0)
                data_repo.save(file_name=destination_file, data=output_file.read())
        # tabula.convert_into(from_file, destination_file, output_format="csv", pages='all',  guess=False)
        return destination_file

    def get_area(self):
        """
        Tabula area coordintates: [top, left, left+width, top+height]. We're setting height for 10 pages, the other
        coordinates are exact and calculated with Mac preview (https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool#grab-coordinates-of-the-table-you-want)
        If we don't set coordinates the results are unpredictable on some bank statements requested exports, moving data
        on 8th or more columns, making it impossible to extract.

        :return:
        """
        area = [300, 11.39, 10000, 582]
        return area

    def extract_data(self, from_file):
        LOGGER.debug(f'Extract data from generated bank statement {from_file}')
        try:
            df = pd.read_csv(data_repo.read_stream(from_file), header=None)
        except pd.errors.ParserError as e:
            LOGGER.error(e, exc_info=True)
            column_names = [f'Unnamed: {i}' for i in range(0, 10)]
            df = pd.read_csv(data_repo.read_stream(from_file), header=None, names=column_names)

        statement = bank_statement(df)
        _df = statement.transform()
        info = statement.bank_statement_info
        destination_file = self.paths.data_file(from_file.replace('.csv', f'_{info.month_short_name}_{info.year}.json'))
        self.data_repo.save(destination_file, bytes(_df.to_json().encode('utf-8')))
        return destination_file


def month_number_to_short_name(month: str):
    datetime_object = datetime.datetime.strptime(month, "%m")
    return datetime_object.strftime("%b")


def find_next_value(row, condition):
    return next(iter([item for item in row if condition(item)]), None)


class BankStatementType(Enum):
    GENERATED = 'generated',
    REQUESTED = 'requested',


@dataclass
class BankStatementInfo:
    month_short_name: str
    year: int
    categories: list[Category]
    separator: str = ','
    statement_type: BankStatementType = BankStatementType.GENERATED
    currency: str = 'RON'

    @staticmethod
    def from_raw_data_generated(df: pd.DataFrame, categories: list[Category]) -> BankStatementInfo:
        date_pattern = "(\d{2}) ([A-Z]+) (\d{4}) - (\d{2}) ([A-Z]+) (\d{4})"
        date_row_index = df.loc[df['Unnamed: 0'].str.startswith('Extras de cont')].index.values[0] + 1
        raw_date = df.iloc[date_row_index]['Unnamed: 0']
        matches = re.match(date_pattern, raw_date)
        groups = list(matches.groups())
        _year = None
        _month = None
        if len(groups) == 6:
            _year = int(groups[2])
            _month = local_date_to_standard(groups[1])
            LOGGER.debug(f'Bank statement generated for month {_month} and year {_year}.')
        return BankStatementInfo(month_short_name=_month, year=_year, categories=categories)

    @staticmethod
    def from_raw_data(df: pd.DataFrame) -> BankStatementInfo:
        cols = {}
        for idx, col in enumerate(df.columns):
            cols[col] = f'Unnamed: {idx}'
        _df = df.rename(columns=cols)
        for col in _df.columns:
            _df[col] = _df[col].fillna('')
            _df[col] = _df[col].astype(str)

        _dfq = _df.query(
            "`Unnamed: 0`.str.contains('RULAJ TOTAL CONT') | `Unnamed: 1`.str.contains('RULAJ TOTAL CONT')")
        is_requested = len(_dfq) > 0
        categories = CategoryService().get_all()
        return BankStatementInfo.from_raw_data_requested(
            _df, categories) if is_requested else BankStatementInfo.from_raw_data_generated(_df, categories)

    @staticmethod
    def from_raw_data_requested(df: pd.DataFrame, categories: list[Category]) -> BankStatementInfo:
        LOGGER.debug('Finding bank statement info...')
        LOGGER.debug(df.to_string())
        date_pattern_from_to = "din (\d{2})/(\d{2})/(\d{4}) - (\d{2})/(\d{2})/(\d{4})"
        date_pattern_from = "din.*(\d{2})/(\d{2})/(\d{4})"
        date_row_index = df.loc[df['Unnamed: 0'].str.startswith('EXTRAS CONT')].index.values[0]
        # date_row_index = df.loc[df['Unnamed: 0'].str.startswith('EXTRAS CONT Numarul')].index.values[0]
        raw_date = find_next_value(df.iloc[date_row_index], lambda val: 'din ' in str(val))
        matches = re.match(date_pattern_from_to, raw_date) or re.match(date_pattern_from, raw_date)
        groups = list(matches.groups())
        _year = None
        _month = None
        if len(groups) >= 3:
            _year = int(groups[2])
            _month = month_number_to_short_name(groups[1])
            LOGGER.debug(f'Bank statement requested for month {_month} and year {_year}.')
        currency = 'RON'
        if len(df.loc[df['Unnamed: 0'].str.contains('EUR Cod IBAN')]) > 0:
            currency = 'EUR'
            LOGGER.debug('Found EUR statement.')

        return BankStatementInfo(month_short_name=_month, year=_year, separator='.',
                                 statement_type=BankStatementType.REQUESTED, categories=categories, currency=currency)


def local_date_to_standard(date: str):
    """
    Short names are localized, therefore we need to adjust to convert to datetime short name.
    """
    return date.lower().replace('ian', 'jan') \
        .replace('mai', 'may') \
        .replace('iun', 'jun') \
        .replace('iul', 'jul') \
        .replace('noi', 'nov')


@dataclass
class BankStatementEntry:
    date: datetime.date
    desc: str
    suma: float
    category: str = 'other'

    def to_df(self):
        return self.__dict__

    @staticmethod
    def from_raw_data(date: str, desc: str, suma: str, bank_statement_info: BankStatementInfo, year=None):
        LOGGER.debug(f'Creating bank entry from [{date}, {desc}, {suma}]')
        _suma = BankStatementEntry.convert_suma_to_float(suma, bank_statement_info.separator)
        if _suma and bank_statement_info.currency == 'EUR':
            _suma = _suma * 5
        std_date = local_date_to_standard(date)
        _year = year or bank_statement_info.year
        _date = datetime.datetime.strptime(f'{std_date}-{_year}', '%d-%b-%Y')
        _category = 'other'
        for category in bank_statement_info.categories:
            if any([key_word in desc.lower() for key_word in category.key_words]):
                _category = category.name
        return BankStatementEntry(date=_date, desc=desc, suma=_suma, category=_category)

    @staticmethod
    def convert_suma_to_float(suma: str, separator: str):
        _suma = suma
        _suma_parts = suma.split(' ')
        if len(_suma_parts) > 0:
            _suma = _suma_parts[-1]
        LOGGER.debug(f'Suma is {suma}, separator is {separator}')
        _suma = float(_suma.replace('.', '').replace(',', '.')) if separator == ',' else float(
            _suma.replace(',', ''))
        return _suma

    @staticmethod
    def find_date(text: str):
        match = re.match(f"^(\d{{2}})-([A-Za-z]{{3}})(.*)", text)
        _date = None
        _text = ''
        # LOGGER.debug(f'Find date from text {text}')
        if match:
            groups = list(match.groups())
            # LOGGER.debug(f'Find date from groups {groups}')

            if len(groups) >= 2:
                _date = f'{groups[0]}-{groups[1]}'
                _text = groups[2] if len(groups) == 3 else None
                LOGGER.debug(f'Found date {_date} with text {_text}')
        return _date, _text

    @staticmethod
    def from_full_entry(row: dict, cols: list, bank_statement_info: BankStatementInfo) -> BankStatementEntry:
        date = row[cols[0]]
        desc = row[cols[1]]
        suma = row[cols[2]]
        return BankStatementEntry.from_raw_data(date=date, desc=desc, suma=suma,
                                                bank_statement_info=bank_statement_info)

    @staticmethod
    def from_first_column_full_entry(entry: dict,
                                     cols: list, bank_statement_info: BankStatementInfo) -> BankStatementEntry:

        match = re.match(f"(\d{{2}}-[A-Za-z]{{3}}) (.*)", entry[cols[0]])
        groups = list(match.groups())
        return BankStatementEntry.from_raw_data(date=groups[0], desc=groups[1],
                                                suma=entry[cols[2]], bank_statement_info=bank_statement_info)

    @staticmethod
    def from_first_column_last_entries(row: dict, last_entries: list, cols: list,
                                       bank_statement_info: BankStatementInfo) -> BankStatementEntry:
        """
        Extract bank statement entry from raw data table multiline entries with date and desc on first column.
        :param last_entries: Previous entries, calculated between star points entries.
        :param row: DataFrame row from raw data table.
        :param cols: DataFrame cols
        :param bank_statement_info:

        :return: Bank statement entry.
        """
        desc = ''
        date = last_entries[-1][cols[0]].split(' ')
        if len(date) > 1:
            desc += ' '.join(date[2:])

        date = date[0]
        suma = last_entries[-1][cols[2]]
        if len(suma) == 0:
            suma = last_entries[-1][cols[1]]
        for entry in last_entries[0:-1]:
            desc += ' ' + entry[cols[0]]
        desc = f'{desc} {row[cols[0]]}'
        return BankStatementEntry.from_raw_data(date=date, desc=desc, suma=suma,
                                                bank_statement_info=bank_statement_info)

    @staticmethod
    def from_second_column_last_entries(row: dict, last_entries: list, cols: list,
                                        bank_statement_info: BankStatementInfo) -> BankStatementEntry:
        """
        Extract bank statement entry from raw data table multiline entries with date and desc on first and second
        column.
        :param last_entries: Previous entries, calculated between star points entries.
        :param row: DataFrame row from raw data table.
        :param cols: DataFrame cols
        :param bank_statement_info:

        :return: Bank statement entry.
        """

        desc = ''
        date = last_entries[-1][cols[0]].split(' ')
        if len(date) > 1:
            desc += ' '.join(date[2:])

        date = date[0]
        suma = last_entries[-1][cols[2]]
        if len(suma) == 0:
            suma = last_entries[-1]['Unnamed: 1'].split(' ')
            if len(suma) > 1:
                desc += ' '.join(date[:2])
            suma = suma[-1]

        for entry in last_entries[0:-1]:
            desc += ' ' + entry[cols[1]]
        desc = f'{desc} {row[cols[1]]}'
        return BankStatementEntry.from_raw_data(date=date, desc=desc, suma=suma,
                                                bank_statement_info=bank_statement_info)


class BankStatementData:
    """
    Handles generated bank statements sent automatically over email, usually card statements in PDF format.
    """

    def __init__(self, df: pd.DataFrame, bank_statement_info: BankStatementInfo):
        self.df = df
        self.cols = ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2']
        self.data_table_start_pattern = 'DATA DESCRIERE'
        self.data_table_end_pattern = 'Alte tranzactii'
        self.bank_statement_info = bank_statement_info

    def col_to_str(self, col):
        self.df[col].fillna('', inplace=True)
        self.df[col] = self.df[col].astype(str)

    def is_full_entry(self, row: dict, last_entries: list) -> bool:
        """
        Check if row contains full bank statement entry.
        :param last_entries: Previous entries, calculated between star points entries.
        :param row: DataFrame row from raw data table

        :return: True or False
        """
        return len(row[self.cols[0]]) > 0 \
               and len(row[self.cols[1]]) > 0 \
               and len(row[self.cols[2]]) > 0 and \
               len(last_entries) == 0

    def is_breakpoint(self, row: dict) -> bool:
        col_0 = row[self.cols[0]]
        is_breakpoint = BankStatementEntry.find_date(col_0)[0] is not None
        if is_breakpoint:
            LOGGER.debug(f'Found breakpoint for {col_0}, {row[self.cols[1]]}, {row[self.cols[2]]}')
        return is_breakpoint

    def is_first_column_full_entry(self, entry: dict, bank_statement_date: BankStatementInfo) -> bool:
        _entry = entry[self.cols[0]]
        is_full_entry = False
        if BankStatementEntry.find_date(_entry):
            is_full_entry = True
        return is_full_entry

    def is_first_column_multi_line_entry(self, row: dict) -> bool:
        """
        Raw data table entries are delimited by star points entry most of the time. On some pages, multi line entries
        containing date and desc are present on first column, on another pages they are present on first and second
        columns.
        :param row: DataFrame row from raw data table
        :return: True or False
        """
        return 'Puncte Star' in row[self.cols[0]]

    def is_second_column_multi_line_entry(self, row: dict) -> bool:
        """
        Raw data table entries are delimited by star points entry most of the time. On some pages, multi line entries
        containing date and desc are present on first column, on another pages they are present on first and second
        columns.
        :param row: DataFrame row from raw data table
        :return: True or False
        """
        return 'Puncte Star' in row[self.cols[1]]

    def is_first_column_multi_line_entry_with_full_entries(self, last_entries: list) -> bool:
        """
        Once we split raw data table multi line entries by star points delimiter, we need to further split full entries
        which don't have star points delimiter.
        :param last_entries: Previous entries, calculated between star points entries.

        :return: True or False
        """
        sum_list = [entry['Unnamed: 2'] for entry in last_entries if len(entry[self.cols[2]]) > 0]
        return True if len(sum_list) > 1 else False

    def find_sections_indexes(self, start_idx, end_idx) -> list[dict]:
        df = self.df
        sections_indexes = []
        sections = ['Cumparaturi la parteneri Star Card', 'Cumparaturi la alti comercianti', 'Alte tranzactii',
                    'Cumparaturi din Puncte Star']
        LOGGER.info('Extracting sections indexes...')
        for idx, section in enumerate(sections):
            section_strt_dfq = df.query(f"`{self.cols[0]}`.str.contains('{section}')"
                                        f"& index > {start_idx}"
                                        f"& index < {end_idx}")
            if len(section_strt_dfq) > 0:
                sections_indexes.append({'section': section, 'start_idx': section_strt_dfq.index.values[0]})
        LOGGER.debug(f'Sections indexes: {sections_indexes}')
        return sections_indexes

    def extract_data_tables(self) -> list[dict]:
        df = self.df

        LOGGER.info('Extracting data tables...')
        start_idx = df.query(f"`{self.cols[0]}`.str.contains('ADRIAN DOLHA')"
                             f"| `{self.cols[0]}`.str.contains('DOLHA ADRIAN')").index.values[0]
        end_idx_dfq = df.query(f"`{self.cols[0]}`.str.contains('LAVINIA DOLHA')")
        if len(end_idx_dfq) == 0:
            end_idx_dfq = df.query(f"`{self.cols[0]}`.str.contains('Sumar tranzactii')")
        end_idx = end_idx_dfq.index.values[0]
        sections_indexes = self.find_sections_indexes(start_idx, end_idx)
        sections_indexes.append({'section': 'last', 'start_idx': end_idx})
        data_tables_indexes = []
        for idx, section_index in enumerate(sections_indexes[:-2]):
            section_start_idx = section_index['start_idx']
            table_start_dfq = df.query(f"`{self.cols[0]}`.str.contains('{self.data_table_start_pattern}')"
                                       f"& index > {section_start_idx}")
            if len(table_start_dfq) > 0:
                start_idx = table_start_dfq.index.values[0] + 1
                next_section_idx = sections_indexes[idx + 1]['start_idx']
                section = section_index['section']
                LOGGER.debug(f"Found section {section}")
                end_idx = next_section_idx
                if end_idx > start_idx:
                    data_tables_indexes.append({'section': section, 'indexes': [start_idx, end_idx]})
        LOGGER.debug(f'Data tabless indexes: {data_tables_indexes}')
        tables = []
        for item in data_tables_indexes:
            tables.append({
                'section': item['section'],
                'table': df.iloc[item['indexes'][0]:item['indexes'][1]]
            })
        return tables

    def transform(self) -> pd.DataFrame:
        LOGGER.debug('Raw df...')
        LOGGER.debug(self.df.to_string())
        for col in self.cols:
            self.col_to_str(col)
        tables = self.extract_data_tables()
        dfs = []
        for item in tables:
            LOGGER.info(f'Processing section {item["section"]}')
            dfs.append(self.transform_table_date_breakpoint(item['table']))
        return pd.concat(dfs, ignore_index=True)

    def extract_entry_from_last_entries(self, last_entries: list) -> BankStatementEntry:
        LOGGER.debug(f'Extract statement from {last_entries}')
        date, desc, suma = '', '', ''
        for entry in last_entries:
            entry_text = str(entry[self.cols[0]])
            _date, _desc = BankStatementEntry.find_date(entry_text)
            if _date is not None:
                date = _date
                if len(_desc) == 0:
                    _desc = entry[self.cols[1]]
                if len(_desc) > 0:
                    desc += " " + _desc
                suma = entry[self.cols[2]]
                if len(suma) == 0:
                    suma = entry[self.cols[1]]
            else:
                _desc_col1 = entry[self.cols[0]]
                _desc_col2 = entry[self.cols[1]]
                desc += " " + (_desc_col1 if len(_desc_col1) > 0 else _desc_col2)
        bank_statement_entry = BankStatementEntry.from_raw_data(date=date, desc=desc, suma=suma,
                                                                bank_statement_info=self.bank_statement_info)
        return bank_statement_entry

    def find_full_entry(self, row) -> BankStatementEntry:
        bank_statement_entry = None
        _date, _desc = BankStatementEntry.find_date(row[self.cols[0]])
        if _date is not None:
            date, desc, suma = _date, _desc, ''
            suma = row[self.cols[2]]
            if len(desc) == 0:
                desc = row[self.cols[1]]
            if len(suma) > 0 and len(desc) > 0:
                LOGGER.debug(f'Extracting full entry {date},{desc},{suma}')
                bank_statement_entry = BankStatementEntry.from_raw_data(date=date, desc=desc, suma=suma,
                                                                        bank_statement_info=self.bank_statement_info)
        return bank_statement_entry

    def transform_table_date_breakpoint(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = pd.DataFrame(columns=['date', 'desc', 'suma'])
        last_entries = []
        LOGGER.debug(f'Processing extracted table:\n {df.to_string()}')
        for index, row in df.iterrows():
            LOGGER.debug(f'Processing row {index}')
            is_breakpoint = self.is_breakpoint(row)
            should_add_entry_to_last_entries = not is_breakpoint
            is_entry_added = False
            if is_breakpoint:
                is_full_entry = False
                bank_statement_entry = self.find_full_entry(row)
                if bank_statement_entry is not None:
                    LOGGER.debug(f'Last entries before full entry {last_entries}')
                    if len(last_entries) > 2 or len(last_entries) == 0:
                        _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
                        is_full_entry = True
                        is_entry_added = True
                    else:
                        should_add_entry_to_last_entries = True

                is_previous_entry = len(last_entries) > 2
                if is_previous_entry:
                    if is_full_entry:
                        LOGGER.debug('Extracting last entry before full entry.')
                        bank_statement_entry = self.extract_entry_from_last_entries(last_entries)
                        last_entries = []
                    else:
                        bank_statement_entry = self.extract_entry_from_last_entries(last_entries[:-1])
                        last_entries = last_entries[-1:]
                        should_add_entry_to_last_entries = True

                    if not bank_statement_entry:
                        LOGGER.debug(f"Couldn't extract entry at breakpoint {row}")
                    _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
                    is_entry_added = True
                should_add_entry_to_last_entries = should_add_entry_to_last_entries or (not is_entry_added)

            if should_add_entry_to_last_entries:
                LOGGER.debug(f'Adding last entry {row}')
                last_entries.append(row)
        # don't miss last entry
        if len(last_entries) > 2:
            LOGGER.debug(f'Extracting last entry from entries:{last_entries}')
            bank_statement_entry = self.extract_entry_from_last_entries(last_entries)
            _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
        return _df

    def transform_table_star_points_breakpoint(self, df: pd.DataFrame) -> pd.DataFrame:
        bank_statement_info = self.bank_statement_info
        _df = pd.DataFrame(columns=['date', 'desc', 'suma'])
        last_entries = []
        LOGGER.debug(f'Processing extracted table:\n {df.to_string()}')
        for index, row in df.iterrows():
            if self.is_full_entry(row, last_entries):
                bank_statement_entry = BankStatementEntry.from_full_entry(row, self.cols, bank_statement_info)
                _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
                last_entries = []
            elif self.is_first_column_multi_line_entry(row):
                if self.is_first_column_multi_line_entry_with_full_entries(last_entries):
                    for entry in last_entries:
                        if self.is_first_column_full_entry(entry, bank_statement_info):
                            bank_statement_entry = BankStatementEntry.from_first_column_full_entry(entry,
                                                                                                   self.cols,
                                                                                                   bank_statement_info)
                            last_entries.remove(entry)
                            _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
                bank_statement_entry = BankStatementEntry.from_first_column_last_entries(row, last_entries, self.cols,
                                                                                         bank_statement_info)
                last_entries = []
                _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
            elif self.is_second_column_multi_line_entry(row):
                bank_statement_entry = BankStatementEntry.from_second_column_last_entries(row, last_entries, self.cols,
                                                                                          bank_statement_info)
                last_entries = []
                _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
            else:
                last_entries.append(row)
        return _df


def is_sum_value(val: float):
    """
    Check if the value found in column is actually sum value. In some cases it's just a ref no.
    :param val:
    :return: True is it's actually sum value.
    """
    return abs(val) < 1000000


def is_float(val):
    if val is None:
        return False
    _val = str(val).replace(',', '')
    try:
        _num_val = float(_val)
        return True if is_sum_value(_num_val) else False
    except ValueError:
        return False


def is_debit_credit(val):
    if not val:
        return False
    _val = str(val).split(' ')
    LOGGER.debug(_val)
    return True if len(_val) == 2 and is_float(_val[0]) and is_float(_val[1]) else False


class BankStatementDataRequested:
    """
    Handles generated bank statements sent automatically over email, usually card statements in PDF format.
    """

    def __init__(self, df: pd.DataFrame, bank_statement_info: BankStatementInfo):
        self.df = df
        cols = {}
        for idx, col in enumerate(df.columns):
            cols[col] = f'Unnamed: {idx}'
        self.cols = list(cols.values())

        self.df.columns = self.cols
        self.data_table_start_pattern = 'SOLD ANTERIOR'
        self.data_table_end_pattern = 'RULAJ TOTAL CONT'
        self.bank_statement_info = bank_statement_info

    def col_to_str(self, col):
        self.df[col].fillna('', inplace=True)
        self.df[col] = self.df[col].astype(str)

    def is_section_end(self, row: dict) -> bool:
        return find_next_value(row, lambda val: 'SOLD FINAL ZI' in val)

    def is_desc_first_column(self, row: dict) -> bool:
        return len(row[self.cols[1]]) == 0

    def is_day_pl(self, row: dict):
        return find_next_value(row, lambda val: 'RULAJ ZI' in val)

    def is_section_footer(self, row: dict) -> bool:
        return self.is_day_pl(row) or self.is_section_end(row)

    def extract_data_tables(self) -> list[dict]:
        df = self.df
        section_start_text = "SOLD ANTERIOR"
        section_end_text = "RULAJ TOTAL CONT"
        LOGGER.info('Extracting data tables...')

        section_strt_dfq = df.query(f"`{self.cols[0]}`.str.contains('{section_start_text}')"
                                    f"& index > 0"
                                    )
        tables = []
        while len(section_strt_dfq) > 0:
            start_idx = section_strt_dfq.index.values[0] + 2
            LOGGER.debug(f'section start index {start_idx}')
            section_end_dfq = df.query(f"(`{self.cols[0]}`.str.contains('{section_end_text}')"
                                       f" | `{self.cols[1]}`.str.contains('{section_end_text}'))"
                                       f"& index > {start_idx}"
                                       )
            LOGGER.debug(f'section end index col 1 {len(section_end_dfq)}')
            # end_idx = start_idx + 1
            if len(section_end_dfq) > 0:
                end_idx = section_end_dfq.index.values[0]
            else:
                end_idx = df.last_valid_index()
            LOGGER.debug(f'section end index {end_idx}')
            section_strt_dfq = df.query(f"`{self.cols[0]}`.str.contains('{section_start_text}')"
                                        f"& index > {end_idx}"
                                        )
            if end_idx > start_idx:
                _df = df.iloc[start_idx:end_idx]
                _df = self.remove_header_footer_between_pages(_df)
                tables.append({'section': {'start_idx': start_idx, 'end_dx': end_idx},
                               'table': _df})
        return tables

    def remove_header_footer_between_pages(self, df: pd.DataFrame) -> pd.DataFrame:
        _df = df
        remove_page_footer = True
        while remove_page_footer:
            remove_page_footer = False
            page_footer_start_row = _df.loc[_df[self.cols[0]].str.contains('BANCA TRANSILVANIA S. A.')]
            if len(page_footer_start_row) > 0:
                start_index = page_footer_start_row.index.values[0]
                page_header_start_row = _df.query(
                    f"`{self.cols[0]}`.str.contains('Data') and index > {start_index}")
                if len(page_header_start_row) == 0:
                    end_index = _df.last_valid_index()
                else:
                    end_index = page_header_start_row.index.values[0] + 1

                if end_index > start_index:
                    remove_page_footer = (end_index > start_index)
                    if remove_page_footer:
                        LOGGER.debug(f'Remove page footer from {start_index} to {end_index}')
                        _df.drop(range(start_index, end_index), inplace=True)
        return _df

    def transform(self) -> pd.DataFrame:
        LOGGER.debug('Raw df...')
        LOGGER.debug(self.df.to_string())
        for col in self.cols:
            self.col_to_str(col)
        tables = self.extract_data_tables()
        dfs = []
        for item in tables:
            LOGGER.info(f'Processing section {item["section"]}')
            dfs.append(self.transform_table(item['table']))
        return pd.concat(dfs, ignore_index=True)

    def transform_table(self, table_df: pd.DataFrame) -> pd.DataFrame:
        for col in self.cols:
            self.col_to_str(col)
        bank_statement_info = self.bank_statement_info
        last_entries = []
        _df = pd.DataFrame(columns=['date', 'desc', 'suma'])
        df = table_df
        date_pattern = "^(\d{2})/(\d{2})/(\d{4})(.*)"
        crt_date = None
        year = bank_statement_info.year
        suma = None
        credit_list = []
        for index, row in df.iterrows():
            # LOGGER.debug(row)
            debit_credit_text = find_next_value(row, is_debit_credit)
            if self.is_day_pl(row):
                LOGGER.debug(f'Debit credit text is {debit_credit_text}')
                debit, credit = debit_credit_text.split(' ') if debit_credit_text is not None else None
                credit = BankStatementEntry.convert_suma_to_float(f'-{credit}', bank_statement_info.separator)
                if credit and credit < 0:
                    credit_list.append(credit)

            suma_text = find_next_value(row, lambda val: is_float(val))
            if suma_text and not (self.is_section_footer(row)):
                if len(last_entries) > 0:
                    bank_statement_entry = self.extract_bank_statement_from_last_entries(bank_statement_info, crt_date,
                                                                                         date_pattern, last_entries,
                                                                                         suma, year)
                    _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
                    last_entries = []
                year = self.find_year(date_pattern, row)
                crt_date = self.find_date(date_pattern, row) or crt_date
                suma = f'-{suma_text}'.replace('--', '-') if suma_text else None
            if not (self.is_section_footer(row)):
                last_entries.append(row)
        # don't miss the last one
        if len(last_entries) > 0:
            bank_statement_entry = self.extract_bank_statement_from_last_entries(bank_statement_info, crt_date,
                                                                                 date_pattern, last_entries,
                                                                                 suma, year)
            _df = _df.append(bank_statement_entry.to_df(), ignore_index=True)
        self.update_credit_entries(_df, credit_list)
        return _df

    def update_credit_entries(self, _df, credit_list):
        """
        In the original PDF credit and debit entries are on separate columns, but for some reason tabula py merges them
        which makes it confusing since you can't figure which is which. There is one way to figure out with pretty good
        accuracy and that is to look at the daily P&L entry which has cummulated debit and credit. In most of the cases
        there won't be more than one credit in a day, therefore it's safe to assume that we can entries which match the
        credit sum are actually credit entries.

        :param _df: Data DataFrame
        :param credit_list: the list of credit entries
        :return: New DataFrame where credit entries have positive values.
        """
        for credit in credit_list:
            LOGGER.debug(f'credit is{credit}')
            _df["suma"] = _df["suma"].apply(lambda val: abs(val) if val == credit else val)

    def extract_bank_statement_from_last_entries(self, bank_statement_info, crt_date, date_pattern, last_entries, suma,
                                                 year=None):
        desc = ''
        for entry in last_entries:
            first_col_desc = self.remove_date_from_desc(date_pattern, entry[self.cols[0]])
            second_col_desc = self.remove_date_from_desc(date_pattern, entry[self.cols[1]])
            desc += ' ' + (first_col_desc or second_col_desc)
        bank_statement_entry = BankStatementEntry.from_raw_data(desc=desc, date=crt_date, suma=suma,
                                                                bank_statement_info=bank_statement_info, year=year)
        return bank_statement_entry

    def remove_date_from_desc(self, date_pattern, desc):
        match = re.match(date_pattern, desc)
        if match:
            groups = list(match.groups())
            desc = groups[3]
        return desc

    def find_date(self, date_pattern, row):
        crt_date = None
        match = re.match(date_pattern, row[self.cols[0]])
        if match:
            groups = list(match.groups())
            if len(groups) >= 3:
                _month = month_number_to_short_name(groups[1])
                crt_date = f'{groups[0]}-{_month}'
        return crt_date

    def find_year(self, date_pattern, row):
        year = None
        match = re.match(date_pattern, row[self.cols[0]])
        if match:
            groups = list(match.groups())
            if len(groups) >= 3:
                year = groups[2]
        return year
