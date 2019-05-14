import datetime
import re

from self_finance.utils import RegexDict


class DateRange:
    """
    obj: wrapper on top of datetime with the intention of having human level interpretability
    """
    _human_date = RegexDict({
        'min': datetime.date.min,
        'max': datetime.date.max,
        'today': datetime.date.today(),
        'yesterday': datetime.date.today() - datetime.timedelta(days=1),

        '\d+ year.? ago': lambda y: datetime.date.today() - datetime.timedelta(days=y * 365),
        '\d+ month.? ago': lambda m: datetime.date.today() - datetime.timedelta(days=m * 30),
        '\d+ week.? ago': lambda w: datetime.date.today() - datetime.timedelta(weeks=w),
        '\d+ day.? ago': lambda d: datetime.date.today() - datetime.timedelta(days=d),

        '\d+ year.? ahead': lambda y: datetime.date.today() + datetime.timedelta(days=y * 365),
        '\d+ month.? ahead': lambda m: datetime.date.today() + datetime.timedelta(days=m * 30),
        '\d+ week.? ahead': lambda w: datetime.date.today() + datetime.timedelta(weeks=w),
        '\d+ day.? ahead': lambda d: datetime.date.today() + datetime.timedelta(days=d),
    })

    def __init__(self, start, end):
        self._org_start, self._org_end = start, end
        # prioritize the human date if the type is a string
        # then prioritize the raw value itself, which presumable is a datetime
        # any misspellings will be handled by the regex pattern match ValueError
        _start = self._human_date[start] or start if isinstance(start, str) else start
        _end = self._human_date[end] or end if isinstance(end, str) else end

        # at this point the values are a datetime or lambda (and guaranteed not a string!)
        # but it only can be a lambda if the original type was a string
        self.start = self._apply_call(start, _start) if isinstance(start, str) else _start
        self.end = self._apply_call(end, _end) if isinstance(end, str) else _end

    def __repr__(self):
        return f'start: {self.start} | end: {self.end}'

    def __eq__(self, other):
        return other and self._org_start == other._org_start \
               and self._org_end == other._org_end

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._org_start, self._org_end))

    def _apply_call(self, key, value):
        if callable(value):
            try:
                first_num = int(re.search(r'\d+', key).group())
                return value(first_num)
            except AttributeError:
                raise AttributeError("No identified integer found at the start of the date range time.")
        else:
            return value
