import logging
import json
import os
import uuid
import pandas as pd

from billy_data.app_context import app_context
from billy_data.provider import BankStatementProvider
from categories_conftest import *
import pytest
from mock import mock, MagicMock
import numpy as np
from billy_data.bank_statements import create_data_paths
from billy_data.config import get_config

LOGGER = logging.getLogger('billy')


@pytest.fixture()
def config_valid():
    config = {
        'yahoo_user': 'yahoo_user',
        'yahoo_password': 'yahoo_password',
        'yahoo_host': 'yahoo_host',
        'yahoo_port': '100',
        'data_bucket': 'test.bucket',
        'card_statement_pdf_password': 'pwd',
        'cognito_user': 'test_user'
    }
    # config_file = f"{os.path.expanduser('~')}/.cloud-projects/billy-local-integration.json"
    config_file = f"{os.path.expanduser('~')}/config.json"
    print(f'Config file is {config_file}')
    if os.path.exists(config_file):
        with open(config_file, "r") as _file:
            _config = dict(json.load(_file))
            for k, v in _config.items():
                os.environ[k] = str(v)
    else:
        for k in config.keys():
            os.environ[k] = config[k]
        _config = os.environ
    os.environ['prometheus_metrics'] = 'False'
    print('Config...')
    print(_config)
    get_config.cache_clear()
    # create_data_paths()

    return _config


@pytest.fixture()
def app_valid(config_valid):
    LOGGER.setLevel(logging.DEBUG)


@pytest.fixture()
def bank_statements_data_repo(categories):
    from billy_data.repo import data_repo
    abs_path = data_repo.abs_path
    with mock.patch('billy_data.bank_statements.data_repo') as _mock:
        # _mock.return_value.get.return_value = json.dumps(categories)
        _mock.abs_path.side_effect = abs_path
        yield _mock


@pytest.fixture()
def bank_statement_provider_valid(config_valid):
    return BankStatementProvider(id=str(uuid.uuid4()),
                                 provider_type='yahoo',
                                 yahoo_user=config_valid.get('yahoo_user'),
                                 yahoo_password=config_valid.get('yahoo_password'),
                                 yahoo_host=config_valid.get('yahoo_host'),
                                 yahoo_port=int(config_valid.get('yahoo_port')),
                                 card_statement_pdf_password=config_valid.get('card_statement_pdf_password'))


@pytest.fixture()
def events_provider_mock(categories, bank_statement_provider_valid):
    with mock.patch('billy_data.events_consumers.BankStatementProviderService') as _service:
        _service.get_all.return_value = [bank_statement_provider_valid]
        yield _service


@pytest.fixture()
def events_consumers_job_service(categories, events_provider_mock):
    with mock.patch('billy_data.events_consumers.job_service') as _mock:
        yield _mock


@pytest.fixture()
def yahoo_config_valid(config_valid):
    return {'user': config_valid['yahoo_user'],
            'password': config_valid['yahoo_password'],
            'host': config_valid['yahoo_host'],
            'port': config_valid['yahoo_port'],
            'card_statement_pdf_password': config_valid['card_statement_pdf_password']}


@pytest.fixture()
def file_mock():
    with mock.patch('billy_data.repo.open') as _mock:
        yield _mock


@pytest.fixture()
def listdir_mock():
    with mock.patch('billy_data.bank_statements.listdir') as _mock:
        yield _mock


@pytest.fixture()
def isfile_mock():
    with mock.patch('billy_data.bank_statements.isfile') as _mock:
        yield _mock


@pytest.fixture()
def pdf_mock():
    with mock.patch('billy_data.bank_statements.pdf') as _mock:
        yield _mock


@pytest.fixture()
def tabula_mock(temp_file_mock):
    with mock.patch('billy_data.bank_statements.tabula') as _mock:
        yield _mock


@pytest.fixture()
def pd_read_csv():
    with mock.patch('billy_data.bank_statements.pd.read_csv') as _pd:
        yield _pd


@pytest.fixture()
def pd_read_json():
    with mock.patch('billy_data.bank_statements.pd.read_json') as _pd:
        yield _pd


@pytest.fixture()
def temp_file_mock():
    with mock.patch('billy_data.bank_statements.tempfile.NamedTemporaryFile') as _mock:
        yield _mock


@pytest.fixture()
def bank_statements_mocks(config_valid, temp_file_mock, bank_statements_data_repo, file_mock, tabula_mock, pdf_mock,
                          pd_read_csv):
    app_context.username = config_valid['cognito_user']
    yield ''


@pytest.fixture()
def bank_statement_df_transformed_json_valid(pd_read_csv, categories):
    df = pd.DataFrame([
        ['food', '2022-06-20', 'glovo entry 1', -1],
        ['food', '2022-06-21', 'glovo entry 2', -2],
        ['phone', '2022-06-21', 'orange', -2],
    ], columns=['category', 'date', 'desc', 'suma'])
    return df.to_json()


@pytest.fixture()
def bank_statement_df_valid(pd_read_csv, categories):
    df = pd.DataFrame([
        ['Extras de cont Star Gold', '', ''],
        ['01 APR 2022 - 30 APR 2022', '', ''],
        ['ADRIAN DOLHA', np.nan, np.nan],
        ['Cumparaturi la parteneri Star Card', np.nan, np.nan],
        ['DATA DESCRIERE', '', ''],

        ['05-APR APPLE.COM/BILL 0800894847 IE; 04-APR 03:47', np.nan, '-5,2'],

        ['Glovo 04APR CJSSW1FH1 BUCURESTI RO; 04-APR 09:27', np.nan, np.nan],
        ['07-APR', np.nan, '-10'],
        ['+0,37 Puncte Star', np.nan, np.nan],

        ['11-APR', 'Glovo 07APR CJ11T9XQ1 BUCURESTI RO; 07-APR 09:52', '-11,0'],

        [np.nan, 'WWW.ORANGE.RO CONTUL-MEU BUCURESTI RO; 07-APR 16:32', np.nan],
        ['11-APR', np.nan, '-15'],
        [np.nan, '+0,44 Puncte Star', np.nan],

        ['XXX; 26-APR 18:45; 1107.9 CZK; 0,2103', np.nan, np.nan],
        ['27-APR', 'RON/XXX -2,01', np.nan],
        [np.nan, '+0,23 Puncte Star', np.nan],

        ['Cumparaturi la alti comercianti', np.nan, np.nan],
        ['Alte tranzactii', np.nan, np.nan],
        ['DATA DESCRIERE', 'SUMA', ''],
        ['16-APR', 'Taxa Serviciu SMS ZK78251578', '-1,0'],

        [np.nan, 'Comision-Plata catre JOHN DOE, cont 367RONCRT0xxxxxxx;', np.nan],
        ['21-APR', 'Transfer din card 4402 ADRIAN DOLHA catre JOHN DOE reprezentand', '-2,0'],
        [np.nan, ': Transfer BT Pay ', np.nan],

        ['Cumparaturi din Puncte Star', np.nan, np.nan],
        ['Sumar tranzactii', np.nan, np.nan],
    ], columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'])
    pd_read_csv.return_value = df
    yield df


@pytest.fixture()
def bank_statement_local_date(pd_read_csv, categories):
    df = pd.DataFrame([
        ['Extras de cont Star Gold', '', ''],
        ['01 APR 2022 - 30 APR 2022', '', ''],
        ['ADRIAN DOLHA', np.nan, np.nan],
        ['Cumparaturi la parteneri Star Card', np.nan, np.nan],
        ['DATA DESCRIERE', '', ''],

        ['01-IAN', 'desc', '-1,0'],
        ['01-MAI', 'desc', '-1,0'],
        ['01-IUN', 'desc1', '-1,0'],
        ['01-IUL', 'desc', '-1,0'],
        ['01-NOI', 'desc', '-1,0'],

        ['Alte tranzactii', np.nan, np.nan],
        ['Sumar tranzactii', np.nan, np.nan],
    ], columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'])
    pd_read_csv.return_value = df
    yield df


@pytest.fixture()
def bank_statement_missing_statements(pd_read_csv, categories):
    df = pd.DataFrame([
        ['Extras de cont Star Gold', '', ''],
        ['01 APR 2022 - 30 APR 2022', '', ''],
        ['ADRIAN DOLHA', np.nan, np.nan],
        ['Cumparaturi la parteneri Star Card', np.nan, np.nan],
        ['DATA DESCRIERE', '', ''],
        ['05-APR APPLE.COM/BILL 0800894847 IE; 04-APR 03:47', np.nan, '-5,2'],
        ['Glovo 04APR CJSSW1FH1 BUCURESTI RO; 04-APR 09:27', np.nan, np.nan],
        ['07-APR', np.nan, '-10'],
        ['+0,37 Puncte Star', np.nan, np.nan],
        ['11-APR', 'Glovo 07APR CJ11T9XQ1 BUCURESTI RO; 07-APR 09:52', '-11,0'],
        [np.nan, 'WWW.ORANGE.RO CONTUL-MEU BUCURESTI RO; 07-APR 16:32', np.nan],
        ['11-APR', np.nan, '-15'],
        [np.nan, '+0,44 Puncte Star', np.nan],
        ['Alte tranzactii', np.nan, np.nan],
        ['DATA DESCRIERE', 'SUMA', ''],
        ['16-APR', 'Taxa Serviciu SMS ZK78251578', '-1,0'],

        [np.nan, 'Comision-Plata catre JOHN DOE, cont 367RONCRT0xxxxxxx;', np.nan],
        ['21-APR', 'Transfer din card 4402 ADRIAN DOLHA catre JOHN DOE reprezentand', '-2.0'],
        [np.nan, ': Transfer BT Pay ', np.nan],

        ['Cumparaturi din Puncte Star', np.nan, np.nan],
        ['Sumar tranzactii', np.nan, np.nan],
    ], columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'])
    pd_read_csv.return_value = df
    yield df


@pytest.fixture()
def bank_statement_requested_valid(pd_read_csv, categories):
    df = pd.DataFrame([
        ['EXTRAS CONT Numarul: 7', '', 'din 01/07/2021 - 31/07/2021'],
        ['Cumparaturi la parteneri Star Card', np.nan, np.nan],
        ['DATA DESCRIERE', np.nan, 'Debit Credit'],
        ['SOLD ANTERIOR', np.nan, '1.0'],
        [np.nan, np.nan, np.nan],

        ['07/07/2021 Plata clienti speciali - canal electronic', np.nan, '31.0'],
        ['08801494 4371760708801494;4371760763RCS -', np.nan, np.nan],
        ['RDS;RO46BTRL0470160100723247;BTRLRO22', np.nan, np.nan],
        ['REF. F13ECUP211880154', np.nan, np.nan],

        ['Plata clienti speciali - canal electronic', np.nan, '21.27'],
        ['9900193159 8300016018469900193159;83000160184664EON ENERGIE ROMANIA', np.nan, np.nan],
        ['(GAZ SI ELECTRI;RO20BTRL0000160100728300;BTRLRO22', np.nan, np.nan],
        ['REF. F13ECUP211880057', np.nan, np.nan],

        ['07/07/2021 RULAJ ZI', np.nan, '52.27 0.00'],
        ['SOLD FINAL ZI', np.nan, '100'],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],

        ['08/07/2021 Transfer intern - canal electronic', np.nan, '10.01'],
        ['Endava shares', np.nan, np.nan],
        ['REF. F13ECIT211890051', np.nan, np.nan],

        ['08/07/2021 RULAJ ZI', np.nan, '10.01 0.00'],
        ['SOLD FINAL ZI', np.nan, '100'],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],

        ['15/07/2021 Incasare OP - canal electronic', np.nan, '11.1'],
        ['C.I.F.:10232;SALARIU IUNIE 2021;1112ENDAVA ROMANIA', np.nan, np.nan],
        ['SRL;056RONSALB191235493;BTRLRO45', np.nan, np.nan],
        ['REF. 066EIIN211961605', np.nan, np.nan],

        ['P2P BTPay', np.nan, '1673.03'],
        ['Transfer din card 1893 ADRIAN DOLHA catre ADRIAN DOLHA reprezentand :', np.nan, np.nan],
        ['Obliga¿ie de plata', np.nan, np.nan],
        ['REF. 000EWAL21196F12M', np.nan, np.nan],

        ['15/07/2021 RULAJ ZI', np.nan, '10.01 11.1'],
        ['SOLD FINAL ZI', np.nan, '100'],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],

        ['26/07/2021 Plata OP intra - canal electronic', np.nan, '873.03'],
        ['cheltuieli iunie 2021 apt F6 plus restante;65Asociatia de Proprietari Armoniei', np.nan, np.nan],
        ['B;RO83BTRLRONCRT0291187701;BTRLRO22', np.nan, np.nan],
        ['REF. F13EINT212070223', np.nan, np.nan],

        ['26/07/2021 RULAJ ZI', np.nan, '10.01 0.00'],
        [
            'BANCA TRANSILVANIA S. A. • Capitalul social: 5.215.917.925 lei (RON) • Nr. Inreg. '
            'Registrul Comertului: J12 / 4155 / 1993 • R.B. - P.J.R - 12 - 019 -',
            np.nan, np.nan],
        ['18.02.1999 • C.U.I. 50 22 670 • SWIFT: BTRLRO22 •  TELEX 31208 TBANK • Tel. +40 264 407150 • '
         'www.bancatransilvania.ro', np.nan, np.nan],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],
        ['Data', 'Descriere', 'Debit Credit'],
        [np.nan, 'SOLD FINAL ZI', '100'],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],

        ['27/07/2021', 'Comision plata OP - canal electronic', '2.5'],
        [np.nan, 'REF. F13EACH212080035', np.nan],

        [np.nan, 'Plata OP inter - canal electronic', '25.01'],
        [np.nan, 'cv fact. 37634;CHECK66Clinica  Medicala Gynera', np.nan],
        [np.nan, 'SRL;RO16BREL0262980313530190;BRELROBU', np.nan],
        [np.nan, 'REF. F13EACH212080035', np.nan],

        ['27/07/2021', 'RULAJ ZI', '25.01 0.0'],
        [np.nan, 'SOLD FINAL ZI', '100'],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],

        ['31/07/2021', 'Abonament BT 24', '5.00'],
        [np.nan, 'REF. F13EACH212080035', np.nan],

        ['31/07/2021', 'RULAJ TOTAL CONT', '100.00 11.01'],
        [np.nan, 'SOLD FINAL CONT', '100'],
        [np.nan, np.nan, np.nan],
    ], columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'])
    pd_read_csv.return_value = df
    yield df


@pytest.fixture()
def bank_statement_requested_currency_eur(pd_read_csv, categories):
    df = pd.DataFrame([
        ['EXTRAS CONT Numarul: 7 EUR Cod IBAN', '', 'din 01/07/2021 - 31/07/2021'],
        ['Cumparaturi la parteneri Star Card', np.nan, np.nan],
        ['DATA DESCRIERE', np.nan, 'Debit Credit'],
        ['SOLD ANTERIOR', np.nan, '1.0'],
        [np.nan, np.nan, np.nan],

        ['07/07/2021 test currency entry', np.nan, '1.0'],


        ['27/07/2021', 'RULAJ ZI', '25.01 0.0'],
        [np.nan, 'SOLD FINAL ZI', '100'],
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],

        ['31/07/2021', 'Abonament BT 24', '5.00'],
        [np.nan, 'REF. F13EACH212080035', np.nan],

        ['31/07/2021', 'RULAJ TOTAL CONT', '100.00 11.01'],
        [np.nan, 'SOLD FINAL CONT', '100'],
        [np.nan, np.nan, np.nan],
    ], columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2'])
    pd_read_csv.return_value = df
    yield df


@pytest.fixture()
def imap_client():
    with mock.patch('billy_data.bank_statements.ImapClient') as _mock:
        yield _mock


@pytest.fixture()
def card_statements_valid(imap_client):
    email = b"""
Subject: Extras de cont Star Gold - Aprilie 2022, NUME: DO**  **AN
From: Banca Transilvania <extrase@btrl.ro>
To: <ADRIANDOLHA@YAHOO.COM>
Reply-to: "Banca Transilvania" <contact@btrl.ro>
Date: Wed, 11 May 2022 02:00:03 GMT
Content-Type: multipart/mixed;
	boundary="--_=_NextPart_002_01C39C9D.5EAC49D8"
Content-Length: 1864720
    """
    imap_client.return_value.search.return_value = 'OK', [b'100']
    imap_client.return_value.fetch.return_value = [['', email]]
    with mock.patch('billy_data.bank_statements.email') as _email:
        _m = MagicMock()
        _email.message_from_string.return_value = _m

        def __str__(self):
            return email.decode('utf-8')

        _m.__str__ = __str__
        parts = [MagicMock()]
        _email.message_from_string.return_value.walk.return_value = parts
        parts[0].get_filename.return_value = 'file_test.pdf'
        yield _email
