"""Agritech: Flask + MySQL farm-record application.

Local/demo prototype only. Do not expose publicly until authentication,
authorization, deployment hardening, and a security review are complete.
"""
import os
import re
import secrets
from contextlib import contextmanager
from datetime import date
from decimal import Decimal, InvalidOperation

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["WTF_CSRF_ENABLED"] = True
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
CSRFProtect(app)
DB_CONFIG = {"host": os.environ.get("DB_HOST", "localhost"), "user": os.environ.get("DB_USER", "root"), "password": os.environ.get("DB_PASSWORD", ""), "database": os.environ.get("DB_NAME", "agritech"), "connection_timeout": 5}


@contextmanager
def database_cursor(dictionary=False, commit=False):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = None
    try:
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        if commit:
            conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def positive_decimal(value, field_name, optional=False, max_value=None):
    if optional and (value is None or str(value).strip() == ""):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    if number.as_tuple().exponent < -2:
        raise ValueError(f"{field_name} must have at most two decimal places.")
    if max_value is not None and number > max_value:
        raise ValueError(f"{field_name} cannot exceed {max_value}.")
    return number


def valid_date(value, field_name):
    if not value:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.")
    if parsed > date.today():
        raise ValueError(f"{field_name} cannot be in the future.")
    return parsed


def database_unavailable():
    app.logger.exception("Database operation failed")
    flash("The database is unavailable. Check its configuration and try again.", "error")
    return render_template("error.html", message="Database unavailable."), 503


@app.route("/")
def index():
    try:
        with database_cursor(dictionary=True) as cursor:
            cursor.execute("""SELECT c.crop_id, c.crop_name, c.season, c.area_acres,
                c.sowing_date, c.expected_yield_kg, f.name AS farmer_name, f.village
                FROM crops AS c JOIN farmers AS f ON c.farmer_id=f.farmer_id
                ORDER BY c.crop_id DESC""")
            crops = cursor.fetchall()
        return render_template("index.html", crops=crops)
    except mysql.connector.Error:
        return database_unavailable()


@app.route("/farmers")
def farmers():
    try:
        with database_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT farmer_id,name,village,phone FROM farmers ORDER BY name")
            rows = cursor.fetchall()
        return render_template("farmers.html", farmers=rows)
    except mysql.connector.Error:
        return database_unavailable()


@app.route("/farmers/add", methods=["GET", "POST"])
def add_farmer():
    if request.method == "POST":
        name, village = request.form.get("name", "").strip(), request.form.get("village", "").strip()
        phone = request.form.get("phone", "").strip()
        if not name or not village or len(name) > 100 or len(village) > 100:
            flash("Name and village are required and must be 100 characters or fewer.", "error")
            return render_template("add_farmer.html"), 400
        if phone and not re.fullmatch(r"[0-9+() .-]{7,15}", phone):
            flash("Enter a valid phone number (7 to 15 allowed characters).", "error")
            return render_template("add_farmer.html"), 400
        try:
            with database_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO farmers (name,village,phone) VALUES (%s,%s,%s)", (name,village,phone or None))
            flash(f"Farmer '{name}' added.", "success")
            return redirect(url_for("farmers"))
        except mysql.connector.Error:
            return database_unavailable()
    return render_template("add_farmer.html")


@app.route("/crops/add", methods=["GET", "POST"])
def add_crop():
    try:
        with database_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT farmer_id,name,village FROM farmers ORDER BY name")
            all_farmers = cursor.fetchall()
    except mysql.connector.Error:
        return database_unavailable()
    if request.method == "POST":
        farmer_id = request.form.get("farmer_id", "").strip()
        crop_name = request.form.get("crop_name", "").strip()
        season = request.form.get("season", "").strip()
        if not farmer_id.isdigit() or not crop_name or len(crop_name) > 100:
            flash("Select a farmer and enter a crop name of at most 100 characters.", "error")
            return render_template("add_crop.html", farmers=all_farmers, today=date.today().isoformat()), 400
        if season not in {"Kharif","Rabi","Zaid"}:
            flash("Select a valid season.", "error")
            return render_template("add_crop.html", farmers=all_farmers), 400
        try:
            area = positive_decimal(request.form.get("area_acres"), "Area", max_value=Decimal("9999.99"))
            expected = positive_decimal(
                request.form.get("expected_yield_kg"),
                "Expected yield",
                optional=True,
                max_value=Decimal("99999999.99"),
            )
            sowing = valid_date(request.form.get("sowing_date"), "Sowing date")
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("add_crop.html", farmers=all_farmers), 400
        try:
            with database_cursor(commit=True) as cursor:
                cursor.execute("""INSERT INTO crops
                    (farmer_id,crop_name,season,area_acres,sowing_date,expected_yield_kg)
                    VALUES (%s,%s,%s,%s,%s,%s)""", (int(farmer_id),crop_name,season,area,sowing,expected))
            flash(f"Crop '{crop_name}' logged.", "success")
            return redirect(url_for("index"))
        except mysql.connector.IntegrityError:
            flash("The selected farmer does not exist. Select a valid farmer.", "error")
            return render_template("add_crop.html", farmers=all_farmers), 400
        except mysql.connector.Error:
            return database_unavailable()
    return render_template("add_crop.html", farmers=all_farmers, today=date.today().isoformat())


@app.route("/crops/delete/<int:crop_id>", methods=["POST"])
def delete_crop(crop_id):
    try:
        with database_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM crops WHERE crop_id=%s", (crop_id,))
            deleted = cursor.rowcount
        flash("Crop entry deleted." if deleted else "Crop entry not found.", "success" if deleted else "error")
        return redirect(url_for("index"))
    except mysql.connector.Error:
        return database_unavailable()


@app.route("/prices")
def prices():
    try:
        with database_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT crop_name,price_per_kg,updated_on FROM market_prices ORDER BY updated_on DESC")
            rows = cursor.fetchall()
        return render_template("prices.html", prices=rows)
    except mysql.connector.Error:
        return database_unavailable()


@app.errorhandler(413)
def request_too_large(_error):
    return render_template("error.html", message="The submitted request is too large."), 413


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", message="The requested page was not found."), 404


if __name__ == "__main__":
    environment = os.environ.get("APP_ENV", "development").lower()
    if environment == "production" and not os.environ.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY before starting in production.")
    app.run(host=os.environ.get("HOST","127.0.0.1"), port=int(os.environ.get("PORT","5000")),
            debug=environment == "development" and os.environ.get("FLASK_DEBUG") == "1")
