from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pymysql
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scholarship_applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                dob DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    conn.close()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend healthy"}), 200

@app.route("/apply", methods=["POST"])
def apply():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    dob = data.get("dob")

    if not name or not email or not dob:
        return jsonify({"message": "Name, email and DOB are required"}), 400

    birth_year = datetime.strptime(dob, "%Y-%m-%d").year

    if birth_year <= 1998:
        return jsonify({
            "eligible": False,
            "message": "Scholarship is not available"
        }), 200

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO scholarship_applications (name, email, dob, status)
            VALUES (%s, %s, %s, %s)
        """, (name, email, dob, "Scholarship Available"))
    conn.commit()
    conn.close()

    return jsonify({
        "eligible": True,
        "message": "Scholarship is available and application stored"
    }), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)