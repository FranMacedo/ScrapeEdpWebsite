setlocal
cd /d %~dp0
@echo off
set /p mess="Enter commit message: "
cmd /k "cd /d venv\Scripts & activate & cd.. & cd.. & git add . & git commit -m "%mess%" & git push origin master & exit"
