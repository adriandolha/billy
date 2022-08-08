import pandas as pd

from billy_api import LOGGER
from billy_api.bank_statements import get_data_df


class StatsApi:
    def expenses_per_month(self) -> dict:
        _df = get_data_df().query('suma < 0')
        LOGGER.debug(_df.to_string())
        _df['year'] = pd.DatetimeIndex(_df['date']).year
        _df['month'] = pd.DatetimeIndex(_df['date']).month
        _df = _df.groupby(['year', 'month'], as_index=False).sum()
        _df['suma'] = _df['suma'].round().abs().astype(int)
        LOGGER.info(f"Return result...")
        LOGGER.debug(_df.to_string())
        return {'columns': _df.columns.values.tolist(), 'items': _df.values.tolist()}

    def expenses_per_month_and_category(self) -> dict:
        _df = get_data_df().query('suma < 0')
        LOGGER.debug(_df.to_string())
        _df['year'] = pd.DatetimeIndex(_df['date']).year
        _df['month'] = pd.DatetimeIndex(_df['date']).month
        _df = _df.groupby(['category', 'year', 'month'], as_index=False).sum()
        _df['suma'] = _df['suma'].round().abs().astype(int)
        LOGGER.info(f"Return result...")
        LOGGER.debug(_df.to_string())
        return {'columns': _df.columns.values.tolist(), 'items': _df.values.tolist()}