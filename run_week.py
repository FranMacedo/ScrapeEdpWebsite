from run_robot import multi_robot
from datetime import datetime as dt

multi_robot(gestao='EGEAC', date_list=[dt.now().date()], replace=True)

multi_robot(gestao='EGEAC', date_list=[dt.now().date()], replace=False)
