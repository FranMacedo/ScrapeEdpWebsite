setlocal
cd /d %~dp0
@echo off
cmd /c "powershell -ExecutionPolicy Bypass -File update_chromedriver.ps1 & cd /d venv\Scripts & activate & cd.. & cd.. & python run_info.py"
cmd /c "git add . & git commit -m "daily update" & git pull origin master & git push origin master & exit"
exit 0
