setlocal
cd /d %~dp0
@echo off
cmd /c "powershell -ExecutionPolicy Bypass -File update_chromedriver.ps1 & cd /d venv\Scripts & activate & python run_info.py"

call git add .
call git commit -m "update info"
call git pull origin master
call git push origin master

