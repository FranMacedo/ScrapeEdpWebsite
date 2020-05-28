# Robot EDP Online
Python Robot to download energy data from [edp website](https://online.edpdistribuicao.pt/login), for different instalations, for different months. Store data as excel files in specific folder.


## Requirements
requires database table that can be accessed through function ```connect_db``` from ```my_functions.py``` OR customize that function.

## Setup
  ```
    git clone
    cd robot_edp_online
    py -m venv venv
    venv/scripts/activate
    pip install -r requirements.txt
  ```
  
## Run
  Edit file ```run_freq.py``` to choose what you want to download and for what month(s).
  Run file ```run_freq.bat``` to update chromedriver (or download if not present) and then it will run ```run_freq.py``` automatically.



