from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

db_path = "attendance.db"
master_file = "master_data.xlsx"


@app.route('/')
def form():
    df_master = pd.read_excel(master_file)

    countries = df_master["Country"].dropna().unique()
    locations = df_master["Location"].dropna().unique()
    employees = df_master["Employee Name"].dropna().unique()
    support_types = df_master["Support Type"].dropna().unique()

    # ✅ Get pending data from database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_name, shift_date, in_time 
        FROM attendance
        WHERE out_time IS NULL OR out_time = ''
    """)

    rows = cursor.fetchall()

    pending = []
    for row in rows:
        pending.append({
            "Employee Name": row[0],
            "Shift Date": row[1],
            "In Time": row[2]
        })

    conn.close()

    return render_template(
        'form.html',
        countries=countries,
        locations=locations,
        employees=employees,
        support_types=support_types,
        pending=pending
    )


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    country = request.form['country']
    location = request.form['location']
    support_type = request.form['support_type']
    shift_date = request.form['shift_date']
    in_time = request.form['in_time']

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ✅ Check existing record
    cursor.execute("""
        SELECT id FROM attendance
        WHERE employee_name=? AND shift_date=? AND (out_time IS NULL OR out_time='')
    """, (name, shift_date))

    match = cursor.fetchone()

    if match:
        # ✅ Update Out Time
        cursor.execute("""
            UPDATE attendance
            SET out_time=?
            WHERE id=?
        """, (in_time, match[0]))
    else:
        # ✅ Insert new record
        cursor.execute("""
            INSERT INTO attendance
            (shift_date, country, location, employee_name, support_type, in_time, out_time)
            VALUES (?, ?, ?, ?, ?, ?, '')
        """, (shift_date, country, location, name, support_type, in_time))

    conn.commit()
    conn.close()

    return redirect(url_for('form', success=1))


@app.route('/update_out_time', methods=['POST'])
def update_out_time():
    name = request.form['name']
    shift_date = request.form['shift_date']
    out_time = request.form['out_time']

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM attendance
        WHERE employee_name=? AND shift_date=? AND (out_time IS NULL OR out_time='')
    """, (name, shift_date))

    match = cursor.fetchone()

    if match:
        cursor.execute("""
            UPDATE attendance
            SET out_time=?
            WHERE id=?
        """, (out_time, match[0]))

    conn.commit()
    conn.close()

    return redirect(url_for('form', success=1))


if __name__ == '__main__':
    app.run(debug=True)