python3 -c "from db import init; init()"
gunicorn -b "0.0.0.0:9900" -w 1 app:app
