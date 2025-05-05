#!/bin/bash

echo "BUILD START"

# Install dependencies with Python 3.9
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt


# Collect static files
python3.9 manage.py collectstatic --noinput

# Apply database migrations
python3.9 manage.py makemigrations
python3.9 manage.py migrate

echo "BUILD END"