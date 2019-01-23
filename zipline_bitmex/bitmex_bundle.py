# pylint: disable = too-many-arguments, unused-argument
"""
Module for building a dataset from BitMEX API.
"""
from logging import getLogger
from typing import Callable, Dict, Iterator, List, Mapping, NoReturn, Text, Tuple

from requests import get
from zipline.assets import AssetDBWriter
from zipline.data.minute_bars import BcolzMinuteBarWriter
from zipline.data.us_equity_pricing import BcolzDailyBarWriter, SQLiteAdjustmentWriter
from zipline.utils.cache import dataframe_cache
from zipline.utils.calendars import register_calendar, TradingCalendar
import numpy as np
import pandas as pd

from .bitmex_calendar import BitmexCalendar

LOGGER = getLogger()


def _bitmex_rest(operation: Text, params: Dict) -> List:
    assert operation[0] == '/'
    res = get('https://www.bitmex.com/api/v1' + operation, params=params)
    if not res.ok:
        raise Exception(res)
    res = res.json()
    if not isinstance(res, list):
        raise Exception(res)
    return res


def _get_metadata(sid_map: List[Tuple[int, Text]]) -> pd.DataFrame:
    metadata = pd.DataFrame(
        np.empty(
            len(sid_map),
            dtype=[
                ('symbol', 'str'),
                ('root_symbol', 'str'),
                ('asset_name', 'str'),
                ('expiration_date', 'datetime64[ns]'),
                ('auto_close_date', 'datetime64[ns]'),
                ('tick_size', 'float'),
                ('multiplier', 'float'),
            ],
        ),
    )
    for sid, symbol in sid_map:
        res = _bitmex_rest('/instrument', {'symbol': symbol})
        assert len(res) == 1
        res = res[0]
        metadata.loc[sid, 'symbol'] = symbol
        metadata.loc[sid, 'root_symbol'] = res['rootSymbol']
        metadata.loc[sid, 'asset_name'] = res['underlying']
        metadata.loc[sid, 'expiration_date'] = pd.to_datetime(res['expiry'])
        metadata.loc[sid, 'auto_close_date'] = pd.to_datetime(res['settle'])
        metadata.loc[sid, 'tick_size'] = res['tickSize']
        metadata.loc[sid, 'multiplier'] = res['lotSize']
    metadata['exchange'] = 'bitmex'
    return metadata


def _get_bars(
        sid_map: List[Tuple[int, Text]],
        start_session: pd.Timestamp,
        end_session: pd.Timestamp,
        cache: dataframe_cache,
        bin_size: Text,
) -> Iterator[Tuple[int, pd.DataFrame]]:
    for sid, symbol in sid_map:
        key = symbol + '-' + bin_size
        if key not in cache:
            cache[key] = pd.DataFrame()
        while cache[key].empty or cache[key].index[-1] < end_session:
            cursor = start_session if cache[key].empty else cache[key].index[-1]
            _res = _bitmex_rest(
                '/trade/bucketed',
                {
                    'binSize': bin_size,
                    'count': 500,
                    'symbol': symbol,
                    'startTime': cursor.isoformat(),
                    'endTime': end_session.isoformat(),
                },
            )
            if not _res:
                break
            res = pd.DataFrame.from_dict(_res)
            res.drop('symbol', axis=1, inplace=True)
            res['timestamp'] = res['timestamp'].map(lambda x: pd.to_datetime(x, utc=True))
            res.set_index('timestamp', inplace=True)
            if not cache[key].empty:
                cache[key] = cache[key].drop(index=cache[key].index[-1])
            cache[key] = pd.concat([cache[key], res])
        yield sid, cache[key]


def _get_minute_bars(
        sid_map: List[Tuple[int, Text]],
        start_session: pd.Timestamp,
        end_session: pd.Timestamp,
        cache: dataframe_cache,
) -> Iterator[Tuple[int, pd.DataFrame]]:
    return _get_bars(sid_map, start_session, end_session, cache, '1m')


def _get_daily_bars(
        sid_map: List[Tuple[int, Text]],
        start_session: pd.Timestamp,
        end_session: pd.Timestamp,
        cache: dataframe_cache,
) -> Iterator[Tuple[int, pd.DataFrame]]:
    return _get_bars(sid_map, start_session, end_session, cache, '1d')


def bitmex_bundle(symbols: List[Text]) -> Callable:
    def ingest(
            environ: Mapping,
            asset_db_writer: AssetDBWriter,
            minute_bar_writer: BcolzMinuteBarWriter,
            daily_bar_writer: BcolzDailyBarWriter,
            adjustment_writer: SQLiteAdjustmentWriter,
            calendar: TradingCalendar,
            start_session: pd.Timestamp,
            end_session: pd.Timestamp,
            cache: dataframe_cache,
            show_progress: bool,
            output_dir: Text,
    ) -> NoReturn:
        sid_map = list(zip(range(len(symbols)), symbols))
        asset_db_writer.write(
            futures=_get_metadata(sid_map),
            exchanges=pd.DataFrame(data=[['bitmex', 'UTC']], columns=['exchange', 'timezone']),
        )
        minute_bar_writer.write(
            _get_minute_bars(sid_map, start_session, end_session, cache),
            show_progress=show_progress,
        )
        daily_bar_writer.write(
            _get_daily_bars(sid_map, start_session, end_session, cache),
            show_progress=show_progress,
        )
        # adjustment_writer.write()
    return ingest


register_calendar('bitmex', BitmexCalendar())
