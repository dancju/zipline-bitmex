import numpy as np
import pandas as pd
from datetime import timedelta
from requests import get
from zipline.utils.calendars import register_calendar
from zipline.utils.cli import maybe_show_progress

from .cal import BitmexCalendar

BITMEX_REST_URL = 'https://www.bitmex.com/api/v1'


def _bitmex_rest(operation: str, params: dict = None) -> list:
	assert operation[0] == '/'
	if params is None:
		params = {}
	res = get(BITMEX_REST_URL+operation, params=params)
	assert res.ok
	res = res.json()
	assert type(res) is list
	return res


def _get_metadata(sid_map: list):
	metadata = pd.DataFrame(
			np.empty(
				len(sid_map),
				dtype=[
					('symbol', 'str'),
					('root_symbol', 'str'),
					('asset_name', 'str'),
					('tick_size', 'float'),
					('expiration_date', 'datetime64[ns]')
					]))
	for sid, symbol in sid_map:
		res = _bitmex_rest('/instrument', {'symbol': symbol})
		assert len(res) == 1
		res = res[0]
		metadata.loc[sid, 'symbol'] = symbol
		metadata.loc[sid, 'root_symbol'] = symbol[:-3]
		metadata.loc[sid, 'asset_name'] = symbol[:-3]
		metadata.loc[sid, 'tick_size'] = res['tickSize']
		metadata.loc[sid, 'expiration_date'] = None if symbol == 'XBTUSD' else pd.to_datetime(res['expiry'])
	metadata['exchange'] = 'bitmex'


def _get_minute_bar(symbol: str, day_start: pd.Timestamp):
	day_end = day_start + timedelta(days=1, seconds=-1)
	res = []
	for _ in range(3):
		_res = _bitmex_rest(
				'/trade/bucketed',
				{
					'binSize': '1m',
					'count': 500,
					'symbol': symbol,
					'startTime': day_start.isoformat(),
					'endTime': day_end.isoformat(),
					'start': len(res)})
		assert len(_res) != 0
		res += _res
	assert len(res) == 24*60
	res = pd.DataFrame.from_dict(res)
	res.drop('symbol', axis=1, inplace=True)
	# I think this is a bug of pandas
	# res['timestamp'] = pd.to_datetime(res['timestamp'], utc=True)
	for i in range(res.shape[0]):
		res.loc[i, 'timestamp'] = pd.to_datetime(res.loc[i, 'timestamp'], utc=True)
	res.set_index('timestamp', inplace=True)
	assert res.shape[1] == 11
	return res


def _get_minute_bars(
		sid_map: list,
		start_session: pd.Timestamp,
		end_session: pd.Timestamp,
		cache):
	for sid, symbol in sid_map:
		for day in pd.date_range(start_session, end_session, freq='D', closed='left'):
			key = symbol+'-'+day.strftime("%Y-%m-%d")
			if key not in cache:
				cache[key] = _get_minute_bar(symbol, day)
			yield sid, cache[key]


def bitmex(symbols: list):
	def ingest(
			environ,
			asset_db_writer,
			minute_bar_writer,
			daily_bar_writer,
			adjustment_writer,
			calendar,
			start_session,
			end_session,
			cache,
			show_progress,
			output_dir):
		sid_map = list(zip(range(len(symbols)), symbols))
		asset_db_writer.write(futures=_get_metadata(sid_map))
		minute_bar_writer.write(
				_get_minute_bars(sid_map, start_session, end_session, cache),
				show_progress=show_progress)
		adjustment_writer.write()
	return ingest

register_calendar('bitmex', BitmexCalendar())
