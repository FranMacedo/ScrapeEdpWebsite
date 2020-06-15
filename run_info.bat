setlocal
cd /d %~dp0
@echo off
cmd /k "powershell -ExecutionPolicy Bypass -File update_chromedriver.ps1 & cd /d venv\Scripts & activate & cd.. & cd.. & python run_info.py & git add . & git commit -m "lala" & git pull origin master & git push origin master & exit"
