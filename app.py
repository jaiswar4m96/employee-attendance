from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

file_path = "attendance.xlsx"
master_file = "master_data.xlsx"


@app.route('/')
def form():
    df_master = pd.read_excel(master_file)

    countries = df_master["Country"].dropna().unique()
    locations = df_master["Location"].dropna().unique()
    employees = df_master["Employee Name"].dropna().unique()
    support_types = df_master["Support Type"].dropna().unique()

    # ✅ Pending records (Out Time blank)
    if os.path.exists(file_path):
        df_att = pd.read_excel(file_path)
        pending = df_att[
            (df_att["Out Time"].isna()) | (df_att["Out Time"] == "")
        ]
    else:
        pending = pd.DataFrame()

    return render_template(
        'form.html',
        countries=countries,
        locations=locations,
        employees=employees,
        support_types=support_types,
        pending=pending.to_dict(orient='records')
    )


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    country = request.form['country']
    location = request.form['location']
    support_type = request.form['support_type']
    shift_date = request.form['shift_date']
    in_time = request.form['in_time']

    if os.path.exists(file_path):
        df = pd.read_excel(file_path, dtype=str)
    else:
        df = pd.DataFrame(columns=[
            "Shift Date", "Country", "Location",
            "Employee Name", "Support Type",
            "In Time", "Out Time"
        ])

    match = df[
        (df["Employee Name"] == name) &
        (df["Shift Date"] == shift_date) &
        ((df["Out Time"].isna()) | (df["Out Time"] == ""))
    ]

    if not match.empty:
        index = match.index[0]
        df.at[index, "Out Time"] = in_time
    else:
        new_data = {
            "Shift Date": shift_date,
            "Country": country,
            "Location": location,
            "Employee Name": name,
            "Support Type": support_type,
            "In Time": in_time,
            "Out Time": ""
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    df.to_excel(file_path, index=False)

    return redirect(url_for('form', success=1))


@app.route('/update_out_time', methods=['POST'])
def update_out_time():
    name = request.form['name']
    shift_date = request.form['shift_date']
    out_time = request.form['out_time']

    if os.path.exists(file_path):
        df = pd.read_excel(file_path, dtype=str)

        match = df[
            (df["Employee Name"] == name) &
            (df["Shift Date"] == shift_date) &
            ((df["Out Time"].isna()) | (df["Out Time"] == ""))
        ]

        if not match.empty:
            index = match.index[0]
            df.at[index, "Out Time"] = out_time

        df.to_excel(file_path, index=False)

    return redirect(url_for('form', success=1))


if __name__ == '__main__':
    app.run(debug=True)