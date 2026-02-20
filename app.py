from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

# allow frontend to connect
CORS(app)


# -----------------------------
# CREATE DATABASE + TABLE
# -----------------------------
def init_db():
    conn = sqlite3.connect('restaurant.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        datetime TEXT,
        people INTEGER,
        message TEXT,
        status TEXT DEFAULT 'PENDING'
    )
    ''')

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# BOOK TABLE (CUSTOMER)
# URL: /book
# -----------------------------
@app.route('/book', methods=['POST'])
def book_table():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        name = data.get("name")
        email = data.get("email")
        datetime_value = data.get("datetime")
        people = data.get("people")
        message = data.get("message", "")

        if not name or not email or not datetime_value or not people:
            return jsonify({"error": "Missing required fields"}), 400

        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()

        c.execute(
            "INSERT INTO bookings (name, email, datetime, people, message, status) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, datetime_value, people, message, "PENDING")
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Booking stored"
        }), 200

    except Exception as e:
        print("BOOK ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# -----------------------------
# GET BOOKINGS (ADMIN PANEL)
# URL: /bookings
# -----------------------------
@app.route('/bookings', methods=['GET'])
def get_bookings():
    try:
        conn = sqlite3.connect('restaurant.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM bookings ORDER BY id DESC")
        rows = c.fetchall()

        bookings = []
        for row in rows:
            bookings.append({
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "datetime": row["datetime"],
                "people": row["people"],
                "message": row["message"],
                "status": row["status"]
            })

        conn.close()
        return jsonify(bookings), 200

    except Exception as e:
        print("FETCH ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# -----------------------------
# UPDATE STATUS (APPROVE/REJECT)
# URL: /update-status/<id>
# -----------------------------
@app.route('/update-status/<int:booking_id>', methods=['PUT'])
def update_status(booking_id):
    try:
        data = request.get_json()
        status = data.get("status")

        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()

        c.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200

    except Exception as e:
        print("UPDATE ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# -----------------------------
# TEST ROUTE
# -----------------------------
@app.route('/')
def home():
    return "Backend Running Successfully!"


if __name__ == "__main__":
    app.run(debug=True, port=5000)