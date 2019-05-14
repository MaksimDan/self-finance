from flask import flash

from self_finance.back_end.date_range import DateRange
from self_finance.constants import Flash


def valid_dr(start, end):
    try:
        DateRange(start, end)
        return True
    except KeyError:
        flash(Flash.DATE_RANGE_FILTER_KEY_ERROR.msg, Flash.DATE_RANGE_FILTER_KEY_ERROR.type)
        return False
