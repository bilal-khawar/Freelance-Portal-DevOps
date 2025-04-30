@echo off

cd .venv/Scripts/
call activate
cd ..
cd ..
cd FreelancePortal
py manage.py makemigrations
py manage.py migrate
py manage.py runserver
pause
