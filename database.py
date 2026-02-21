import sqlite3

def create_database():
    # This creates a solid file named 'attendance.db' in your folder
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Ledger 1: The Students Vault
    # We save their Roll No, Name, and their mathematical Face Data here
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            face_encoding TEXT NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ledger 2: The Daily Attendance Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (roll_no) REFERENCES students (roll_no)
        )
    ''')

    conn.commit()
    conn.close()
    print("Vault Secured: Database and Tables created successfully!")

# This line tells Python to run the function if we execute this file
if __name__ == "__main__":
    create_database()