# robot_edp_online
Python Robot to download energy data from edp, for different instalations, for different months. Store data as excel files in specific folder.


## Requirements
requires database table that can be accessed through function '''connect_db''' from '''my_functions.py'''.

## Setup
  ''' 
    git clone
    cd robot_edp_online
    py -m venv venv
    venv/scripts/activate
    pip install -r requirements.txt
  '''
  
  run file '''run_week.bat''' to download files for the current month
  edit file '''run_week.py''' to change what to download and on wich date.

