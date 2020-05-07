from run_robot import multi_robot
from datetime import datetime as dt
import calendar
from dateutil.relativedelta import relativedelta

today_date = dt.now().date()
if today_date.day < 10:
	date_list = [today_date - relativedelta(months=1), today_date]
else:
	date_list = [today_date]


multi_robot(gestao='EGEAC', date_list=date_list, replace=True)

multi_robot(gestao='EGEAC', date_list=date_list, replace=False)


multi_robot(gestao='SCML', date_list=date_list, replace=True)

multi_robot(gestao='SCML', date_list=date_list, replace=False)
