setlocal
cd /d %~dp0
@echo off
cmd /k "powershell -ExecutionPolicy Bypass -File update_chromedriver.ps1 & cd /d venv\Scripts & activate & cd.. & cd.. & python py_scripts/run_info.py & git add . & git commit -m "INFO update" & git pull origin master & git push origin master & exit"
