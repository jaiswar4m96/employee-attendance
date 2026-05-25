import sqlite3

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_date TEXT,
    country TEXT,
    location TEXT,
    employee_name TEXT,
    support_type TEXT,
    in_time TEXT,
    out_time TEXT
)
''')

conn.commit()
conn.close()

print("✅ Database created successfully")