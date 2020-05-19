setlocal
cd /d %~dp0
@echo off
set /p mes="Enter commit message: "
cmd /k "cd /d venv\Scripts & activate & cd.. & cd.. & git add . & git commit -m "+%id%+" & git push origin master & exit"
