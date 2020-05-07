from run_robot import multi_robot
from datetime import datetime as dt
import calendar
from dateutil.relativedelta import relativedelta

dwnld_date = dt.now().date()
if dwnld_date.day == 1:
	date_list = [dwnld_date - relativedelta(months=1), dwnld_date]
else:
	date_list = [dwnld_date]


multi_robot(gestao='EGEAC', date_list=[dt.now().date()], replace=True)

multi_robot(gestao='EGEAC', date_list=[dt.now().date()], replace=False)


multi_robot(gestao='SCML', date_list=[dt.now().date()], replace=True)

multi_robot(gestao='SCML', date_list=[dt.now().date()], replace=False)
