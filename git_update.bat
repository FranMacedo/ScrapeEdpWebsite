setlocal
cd /d %~dp0
@echo off
set /p id="Enter ID: "
cmd /k "cd /d venv\Scripts & activate & cd.. & cd.. & git add . & git commit -m "daily update" & git push origin master & exit"
