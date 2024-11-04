import sqlite3


def Create_Databse():

    ##### Room Table #####
    conn = sqlite3.connect('classroom_management.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS room (
            id TEXT PRIMARY KEY, 
            name TEXT UNIQUE, 
            type TEXT, 
            floor TEXT, 
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

    ##### Teacher Table #####
    conn = sqlite3.connect('classroom_management.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS teacher (
            id TEXT PRIMARY KEY, 
            name TEXT, 
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

    ##### Booking Table #####
    conn = sqlite3.connect('classroom_management.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            id TEXT PRIMARY KEY UNIQUE ,
            teacher TEXT,
            room TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT
        )
    """)
    conn.commit()
    conn.close()


def fetch_data_booking_with_selected_date(date):
    conn = sqlite3.connect('classroom_management.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM booking WHERE date=?", (date,))
    data = cur.fetchall()
    conn.close()
    return data


def check_type_room(room: str) -> str:
    conn = sqlite3.connect('classroom_management.db')
    cur = conn.cursor()
    cur.execute("SELECT type FROM room WHERE name=?", (room,))
    data = cur.fetchone()
    conn.close()
    return data[0] if data else None