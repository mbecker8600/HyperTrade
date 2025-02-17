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
            if time.time() < datetime.time(9, 30, tzinfo=self.tz):
                return Event(
                    event_type=EVENT_TYPE.MARKET_OPEN,
                    time=self.calendar.next_open(time).tz_convert(self.tz),
                )

            elif time.time() < datetime.time(16, 0, tzinfo=self.tz):
                return Event(
                    event_type=EVENT_TYPE.MARKET_CLOSE,
                    time=self.calendar.next_close(time).tz_convert(self.tz),
                )
            else:
                return Event(
                    event_type=EVENT_TYPE.MARKET_OPEN,
                    time=self.calendar.next_open(time).tz_convert(self.tz),
                )
        else:
            raise NotImplementedError("Only daily frequency is supported")
