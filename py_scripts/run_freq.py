from func.run_robot import multi_robot
from datetime import datetime as dt
import calendar
from dateutil.relativedelta import relativedelta

today_date = dt.now().date()


if today_date.day < 10:
	date_list = [today_date - relativedelta(months=1), today_date]
else:
	date_list = [today_date]


if today_date == dt(2020, 5, 29).date():
	date_list = ['2020-01', '2020-02', '2020-03', '2020-04']
	multi_robot(gestao='CML', date_list=date_list, replace=True)
	# from robot_info import get_info
	# get_info(gestao='cml', get_new=True)
else:
	multi_robot(gestao='EGEAC', date_list=date_list, replace=True)
	multi_robot(gestao='SCML', date_list=date_list, replace=True)
	multi_robot(gestao='CML', date_list=date_list, replace=True)
