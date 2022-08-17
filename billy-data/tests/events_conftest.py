import json

import numpy as np
import pandas as pd
import pytest
from mock import mock, MagicMock


@pytest.fixture()
def collect_event_valid():
    return {'op': 'collect', 'username': 'test_user', 'search_criteria':
        {
            'subjects':
                [
                    'Extras de cont Star Gold - Februarie 2022'
                ],
            'since': '11-Jul-2021'
        }
            }


@pytest.fixture()
def transform_event_valid():
    return {
        'op': 'transform',
        'username': 'test_user',
        'file': 'test_file.json'
    }
