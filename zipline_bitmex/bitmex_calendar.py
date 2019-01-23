from datetime import time
from pytz import timezone

from pandas.tseries.offsets import CustomBusinessDay
from zipline.utils.calendars import TradingCalendar
from zipline.utils.memoize import lazyval


class BitmexCalendar(TradingCalendar):
    @property
    def name(self):
        return "bitmex"

    @property
    def tz(self):
        return timezone('UTC')

    @property
    def open_times(self):
        return [(None, time(0, 0))]

    @property
    def close_times(self):
        return [(None, time(23, 59))]

    @lazyval
    def day(self):
        return CustomBusinessDay(weekmask='Mon Tue Wed Thu Fri Sat Sun')
