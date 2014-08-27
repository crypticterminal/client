import calendar
from datetime import datetime, date, time, timedelta


class Schedule(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.time = time(*kwargs.get('time'))
        self.files = kwargs.get('files', [])
        self.databases = kwargs.get('db', [])
        self.prev_backup = None
        self.next_backup = self.get_next()
        self.exclude = False
    
    def __cmp__(self, other):
        return cmp(self.next_backup, other.next_backup)

    def get_next(self):
        return datetime.combine(date.today(), self.time)

    def update(self, **kwargs):
        self.time = time(*kwargs.get('time'))
        self.files = kwargs.get('files', [])
        self.databases = kwargs.get('db', [])
        self.next_backup = self.get_next()

    def done(self):
        self.prev_backup = datetime.now()
        self.next_backup = self.get_next()


class DailySchedule(Schedule):
    def __init__(self, **kwargs):
        self.period = kwargs.pop('day')
        super(DailySchedule, self).__init__(**kwargs)

    def get_next(self):
        if not self.prev_backup:
            return super(DailySchedule, self).get_next()
        next_date = self.prev_backup.date() + timedelta(days=self.period)
        return datetime.combine(next_date, self.time)

    def update(self, **kwargs):
        self.period = kwargs.pop('day')
        super(DailySchedule, self).update(**kwargs)


class WeeklySchedule(Schedule):
    def __init__(self, **kwargs):
        self.days = self._convert_days(kwargs.pop('days'))
        super(WeeklySchedule, self).__init__(**kwargs)

    def _convert_days(self, days):
        d = []
        for i in range(7):
            if days & 1 << i:
                d.append(i)
        return d

    def get_next(self):
        today = date.today()
        today_index = today.isoweekday() % 7
        curr_week = filter(lambda x, t=today_index: x >= t, self.days)
        if self.prev_backup and self.prev_backup.date() == today:
            curr_week = curr_week[1:]
        next_day = curr_week[0] if curr_week else self.days[0] + 7
        next_date = today + timedelta(days=next_day-today_index)
        return datetime.combine(next_date, self.time)

    def update(self, **kwargs):
        self.days = self._convert_days(kwargs.pop('days'))
        super(WeeklySchedule, self).update(**kwargs)


class MonthlySchedule(Schedule):
    def __init__(self, **kwargs):
        self.day = kwargs.pop('day')
        super(MonthlySchedule, self).__init__(**kwargs)

    def get_next(self):
        today = date.today()
        month = today.month if self.day >= today.day else today.month + 1
        year = today.year if month >= today.month else today.year + 1
        if self.day >= 29:
            day = min(calendar.monthrange(year, month)[1], self.day)
        else:
            day = self.day
        return datetime(year, month, day, self.time.hour, self.time.minute)

    def update(self, **kwargs):
        self.day = kwargs.pop('day')
        super(MonthlySchedule, self).update(**kwargs)
