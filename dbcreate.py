import sqlite3

def create_tables():
    conn = sqlite3.connect("db_mail_face_login.db")
    cursor = conn.cursor()

    # ✅ Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            usr_name TEXT NOT NULL,
            usr_email TEXT UNIQUE NOT NULL,
            usr_mobile TEXT NOT NULL,
            usr_pass TEXT NOT NULL,
            usr_type TEXT NOT NULL,
            usr_ids TEXT NOT NULL
        );
    ''')

    # ✅ Create Face Encryption Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encrypt (
            key_ TEXT NOT NULL,
            status_ TEXT NOT NULL
        );
    ''')

    # ✅ Create Send & Receive Emails Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS send_receive (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            _to TEXT NOT NULL,
            _from TEXT NOT NULL,
            _subject TEXT NOT NULL,
            _date TEXT NOT NULL,
            _DataFile TEXT NOT NULL,
            _FolderName TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()
    print("All tables created successfully!")

# Run the function to create tables
create_tables()
