import datetime

import exchange_calendars as xcals
import pytz
from pandas import Timestamp

from hypertrade.libs.simulator.event.types import EVENT_TYPE, Event, Frequency


class MarketEvents:
    """Handles market events and provides the next market event after a given time."""

    def __init__(
        self,
        exchange: str = "XNYS",
        frequency: Frequency = Frequency.DAILY,
        tz: str = "America/New_York",
    ) -> None:
        """
        Args:
            exchange (ExchangeCalendar string): The exchange to get the calendar for.
            frequency (Frequency): The frequency of the market events.
            tz (pytz.timezone string): The timezone to use for the market events.

        Raises:
            ValueError
                If `start` is earlier than the earliest supported start date.
                If `end` is later than the latest supported end date.
                If `start` parses to a later date than `end`.
            xcals.errors.InvalidCalendarName
                If name does not represent a registered calendar.
        """
        self.calendar: xcals.ExchangeCalendar = xcals.get_calendar(exchange)
        self.frequency = frequency
        self.tz = pytz.timezone(tz)

    def next_market_event(self, time: Timestamp) -> Event[None]:
        """
        Returns the next market event after the given time.
        """
        if self.frequency == Frequency.DAILY:
            open_time = self.calendar.next_open(time).tz_convert(self.tz)
            # Account when the current time being passed is the close time
            close_time = (
                self.calendar.next_close(time).tz_convert(self.tz)
                if self.calendar.next_close(time.normalize()) != time
                else time.tz_convert(self.tz)
            )
            pre_open_time = open_time - datetime.timedelta(minutes=15)
            post_close_time = close_time + datetime.timedelta(minutes=15)

            times_events = [
                (pre_open_time, EVENT_TYPE.PRE_MARKET_OPEN),
                (open_time, EVENT_TYPE.MARKET_OPEN),
                (close_time, EVENT_TYPE.MARKET_CLOSE),
                (post_close_time, EVENT_TYPE.POST_MARKET_CLOSE),
            ]
            future_times = [(t, e) for (t, e) in times_events if t > time]
            next_time, next_type = min(future_times, key=lambda x: x[0])
            return Event(event_type=next_type, time=next_time)
        else:
            raise NotImplementedError("Only daily frequency is supported")
