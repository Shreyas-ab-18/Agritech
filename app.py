"""
Agritech
--------
A Flask + MySQL application for farmers to register, log the crops they are
growing each season, and check current market prices.

Configure DB credentials via environment variables (see README) before running.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "agritech"),
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT crops.crop_id, crops.crop_name, crops.season, crops.area_acres,
               crops.sowing_date, crops.expected_yield_kg,
               farmers.name AS farmer_name, farmers.village
        FROM crops
        JOIN farmers ON crops.farmer_id = farmers.farmer_id
        ORDER BY crops.crop_id DESC
    """)
    crops = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", crops=crops)


@app.route("/farmers")
def farmers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM farmers ORDER BY name")
    all_farmers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("farmers.html", farmers=all_farmers)


@app.route("/farmers/add", methods=["GET", "POST"])
def add_farmer():
    if request.method == "POST":
        name = request.form["name"].strip()
        village = request.form["village"].strip()
        phone = request.form.get("phone", "").strip()

        if not name or not village:
            flash("Name and village are required.")
            return redirect(url_for("add_farmer"))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO farmers (name, village, phone) VALUES (%s, %s, %s)",
            (name, village, phone),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Farmer '{name}' added.")
        return redirect(url_for("farmers"))

    return render_template("add_farmer.html")


@app.route("/crops/add", methods=["GET", "POST"])
def add_crop():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        farmer_id = request.form["farmer_id"]
        crop_name = request.form["crop_name"].strip()
        season = request.form["season"]
        area_acres = request.form["area_acres"]
        sowing_date = request.form.get("sowing_date") or None
        expected_yield_kg = request.form.get("expected_yield_kg") or None

        cursor.execute(
            """INSERT INTO crops (farmer_id, crop_name, season, area_acres, sowing_date, expected_yield_kg)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (farmer_id, crop_name, season, area_acres, sowing_date, expected_yield_kg),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Crop '{crop_name}' logged.")
        return redirect(url_for("index"))

    cursor.execute("SELECT farmer_id, name, village FROM farmers ORDER BY name")
    all_farmers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("add_crop.html", farmers=all_farmers)


@app.route("/crops/delete/<int:crop_id>", methods=["POST"])
def delete_crop(crop_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM crops WHERE crop_id = %s", (crop_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Crop entry deleted.")
    return redirect(url_for("index"))


@app.route("/prices")
def prices():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM market_prices ORDER BY updated_on DESC")
    all_prices = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("prices.html", prices=all_prices)


if __name__ == "__main__":
    app.run(debug=True)
