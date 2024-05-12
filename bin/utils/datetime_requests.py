from datetime import datetime, time

import pandas as pd
import dateutil.tz as dtz

from bin.models.zone import Zone


class DatetimeRequests:
    @staticmethod
    def to_timestamp(dt: datetime, bid_zone: Zone) -> pd.Timestamp:
        dt_input = dt.date()
        local_tz: str = bid_zone.country.tz_
        dt_output = datetime.combine(dt_input, time=time(0, 0))
        dt_output = dt_output.astimezone(dtz.gettz(local_tz))
        return pd.Timestamp(dt_output)
