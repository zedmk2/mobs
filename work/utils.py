from calendar import HTMLCalendar
from datetime import datetime as dtime, date, time
import datetime
from work.models import Shift
import calendar
from django.urls import reverse, reverse_lazy

class ShiftCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super(ShiftCalendar, self).__init__()
        self.events = events

    def formatday(self, day, weekday, events):
        """
        Return a day as a table cell.
        """
        events_from_day = events
        events_html = "<ul>"
        for event in events_from_day:
            if event.date.day == day:
                events_html +=  event.get_quick_url() + " (" + str(len(event.jobs_in_shift.all()))+ ")" + "<br> <ul class='calendar-job-list'>"
                for job in event.jobs_in_shift.all()[:3]:
                    events_html += "<li class='calendar-job-list-item'>" + str(job.job_location.name) + "</li>"
                events_html += "</ul>"
        events_html += "</ul>"
        try:
            date_summary = date(self.theyear,self.themonth,day)
        except:
            date_summary = date(self.theyear,self.themonth,1)
        date_url = reverse('work:date_summary', kwargs={'date_summary':date_summary})
        date_html = u'<a class="calendar-date" href="%s">%s</a>' % (date_url, day)

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s">%s% s</td>' % (self.cssclasses[weekday], date_html , events_html)

    def formatweek(self, theweek, events):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, events) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        self.theyear =theyear
        self.themonth=themonth
        end_of_month_number =  calendar.monthrange(theyear, themonth)[1]
        start = date(theyear,themonth,1)
        end = start.replace(day=end_of_month_number)

        events = Shift.objects.filter(date__lte=end).filter(date__gte=start).prefetch_related('jobs_in_shift').prefetch_related('jobs_in_shift__job_location').prefetch_related('driver').prefetch_related('helper')
        # events = events.values()
        v = []
        a = v.append
        a('<table border="1" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, events))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
