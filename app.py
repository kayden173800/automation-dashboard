from flask import Flask, render_template, request
import os
import sqlite3
import pandas as pd
from database import init_db

app = Flask(__name__)
init_db()

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files.get("file")

    if not file or file.filename == "":
        return "No file selected"

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    df = pd.read_csv(file_path)
    total_rows = len(df)

    if "salary" in df.columns:
        avg_salary = float(df["salary"].mean())
        max_salary = float(df["salary"].max())
        min_salary = float(df["salary"].min())
    else:
        avg_salary = max_salary = min_salary = None

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO uploads (filename, total_rows, avg_salary, max_salary, min_salary)
        VALUES (?, ?, ?, ?, ?)
    """, (file.filename, total_rows, avg_salary, max_salary, min_salary))

    conn.commit()
    conn.close()

    return f"""
    <h2>File processed successfully</h2>
    <p>File: {file.filename}</p>
    <p>Total Rows: {total_rows}</p>
    <p>Avg Salary: {avg_salary}</p>
    <p>Max Salary: {max_salary}</p>
    <p>Min Salary: {min_salary}</p>
    """


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM uploads")
    rows = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)