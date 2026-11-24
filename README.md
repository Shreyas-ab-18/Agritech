# AgriTech

A Flask + MySQL farm-record application for registering farmers, recording crop activity by season, and viewing market-price entries.

> **Educational/local prototype.** This version has no user accounts or role-based access control. Do not expose it publicly or store real personal/farm data until authentication, authorization, backups, and production deployment controls are implemented.

## Features
- Farmer registration and farmer directory
- Crop records linked to farmers
- Kharif, Rabi, and Zaid seasons
- Optional sowing date and expected yield
- Market-price listing
- Parameterized SQL, server-side validation, CSRF protection, and safe database resource cleanup

## Requirements
- Python 3.10+
- MySQL 8+

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
mysql -u root -p < schema.sql
```
Set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and a long random `SECRET_KEY` in your environment before running. The application does not automatically load a `.env` file.

## Run locally
```bash
python app.py
```
Open http://127.0.0.1:5000.

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Routes
| Route | Method | Purpose |
|---|---|---|
| `/` | GET | List crop records |
| `/farmers` | GET | List farmers |
| `/farmers/add` | GET, POST | Register a farmer |
| `/crops/add` | GET, POST | Add a crop record |
| `/crops/delete/<id>` | POST | Delete a crop record |
| `/prices` | GET | View market-price entries |

## Security and limitations
- State-changing forms use Flask-WTF CSRF protection.
- SQL statements use placeholders.
- Database cursors and connections close on success and failure.
- CSRF protection is not authentication. Login and role-based authorization are not implemented.
- Before deployment, add authentication, authorization, HTTPS, a production WSGI server, restricted DB permissions, backups, monitoring, and managed secrets. Do not use Flask's development server in production.
