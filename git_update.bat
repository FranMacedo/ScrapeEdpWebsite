setlocal
cd /d %~dp0
@echo off
set /p mess="Enter commit message: "
cmd /k "git add . & git commit -m "%mess%" & git pull origin master & git push origin master & exit"
