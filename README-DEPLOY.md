Deployment notes

1) Local run (development)
- Create virtualenv: python -m venv .venv
- Activate: .venv\\Scripts\\Activate.ps1 (PowerShell)
- Install: pip install -r requirements.txt
- Copy config/clubhub_credentials.example.py -> config/clubhub_credentials.py and fill in secrets.
- Run: $env:PYTHONPATH='.'; .venv\\Scripts\\python.exe clean_dashboard.py

2) Docker
- docker build -t gym-bot:latest .
- docker run -p 5000:5000 --env-file .env -d gym-bot:latest

3) Heroku
- git push heroku main
- set environment vars on Heroku using `heroku config:set SECRET_KEY=...`

4) Notes
- Do NOT commit config/clubhub_credentials.py or any secrets to git. Use .env or platform secret management.
