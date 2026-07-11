# Agritech

A database-driven farm management web app built with Python (Flask) and
MySQL. Farmers can be registered, their crops logged per season, and current
market prices browsed.

## Schema
Three related tables (`farmers`, `crops`, `market_prices`) — see `schema.sql`.
`crops.farmer_id` is a foreign key into `farmers`, modeling a one-to-many
relationship between a farmer and the crops they grow.

## Setup
```bash
pip install -r requirements.txt

# create the database and tables
mysql -u root -p < schema.sql
```

Set your DB credentials as environment variables (defaults assume local root
with no password):
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=agritech
```

## Run it
```bash
python app.py
```
Visit `http://127.0.0.1:5000`.

## Routes
| Route | Description |
|---|---|
| `/` | List all logged crops |
| `/farmers` | List registered farmers |
| `/farmers/add` | Register a new farmer |
| `/crops/add` | Log a crop for a farmer |
| `/crops/delete/<id>` | Delete a crop entry |
| `/prices` | View market prices |
