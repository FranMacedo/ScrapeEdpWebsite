from run_robot import multi_robot
from datetime import datetime as dt
import calendar
from dateutil.relativedelta import relativedelta

today_date = dt.now().date()


if today_date.day < 10:
	date_list = [today_date - relativedelta(months=1), today_date]
else:
	date_list = [today_date]

if today_date.day == 19 and today_date.month == 5 and today_date.year == 2020:
	date_list = ['2020-01', '2020-02', '2020-03', '2020-04']
	multi_robot(gestao='CML', date_list=date_list, replace=True)
else:
	multi_robot(gestao='EGEAC', date_list=date_list, replace=True)
	multi_robot(gestao='SCML', date_list=date_list, replace=True)
	multi_robot(gestao='CML', date_list=date_list, replace=True)
