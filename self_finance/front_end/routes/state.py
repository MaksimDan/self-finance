from self_finance.constants import Defaults


class State:
    date_range_start = Defaults.DATE_RANGE_START_DEFAULT
    date_range_end = Defaults.DATE_RANGE_END_DEFAULT

    @staticmethod
    def as_dict_helper(main_class, secondary_class=None, excluded=None):
        excluded = {} if excluded is None else excluded
        secondary_class = vars(secondary_class) if secondary_class is not None else {}
        return {k: v for k, v in {**vars(main_class), **secondary_class, **vars(State)}.items()
                if not k.startswith('_')
                and k not in excluded}
