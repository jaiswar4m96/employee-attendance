from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pandas as pd
import requests

app = Flask(__name__)
app.secret_key = "secret123"  # for session

db_path = "attendance.db"
master_file = "master_data.xlsx"

# ✅ LOGIN CREDENTIAL
USERNAME = "Test.allied@1234.net"
PASSWORD = "Test"

# ✅ LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        if user == USERNAME and pwd == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('form'))
        else:
            return render_template('login.html', error="Invalid credentials ❌")

    return render_template('login.html')


# ✅ FORM PAGE
@app.route('/form')
def form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    df_master = pd.read_excel(master_file)

    countries = df_master["Country"].dropna().unique()
    locations = df_master["Location"].dropna().unique()
    employees = df_master["Employee Name"].dropna().unique()
    support_types = df_master["Support Type"].dropna().unique()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_name, shift_date, in_time 
        FROM attendance
        WHERE out_time IS NULL OR out_time = ''
    """)

    rows = cursor.fetchall()
    conn.close()

    pending = []
    for row in rows:
        pending.append({
            "Employee Name": row[0],
            "Shift Date": row[1],
            "In Time": row[2]
        })

    return render_template(
        'form.html',
        countries=countries,
        locations=locations,
        employees=employees,
        support_types=support_types,
        pending=pending
    )


# ✅ SUBMIT
FLOW_URL = "https://default2f46c04048e34eb88fbf418417f644.01.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/f802d3985d8a4c99adcfc68cdd44e37e/triggers/manual/paths/invoke?api-version=1"

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    country = request.form['country']
    location = request.form['location']
    support_type = request.form['support_type']
    shift_date = request.form['shift_date']
    in_time = request.form['in_time']

    # ✅ Send data to Power Automate
    data = {
        "shift_date": shift_date,
        "country": country,
        "location": location,
        "employee_name": name,
        "support_type": support_type,
        "in_time": in_time,
        "out_time": ""
    }

    try:
        requests.post(FLOW_URL, json=data)
    except:
        return "Error sending data to Power Automate"

    return redirect(url_for('form', success=1))


# ✅ UPDATE OUT TIME
@app.route('/update_out_time', methods=['POST'])
def update_out_time():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    name = request.form['name']
    shift_date = request.form['shift_date']
    out_time = request.form['out_time']

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance
        SET out_time=?
        WHERE employee_name=? AND shift_date=? AND (out_time IS NULL OR out_time='')
    """, (out_time, name, shift_date))

    conn.commit()
    conn.close()

    return redirect(url_for('form'))


# ✅ LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)