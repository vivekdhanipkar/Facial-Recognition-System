import sqlite3

class DatabaseConnection:
    def __init__(self, db_path="db_mail_face_login.db"):
        self.db_path = db_path
        self.enable_wal_mode()  # Enable WAL mode on startup

    def connect(self):
        """Create a new SQLite connection (Thread-Safe)."""
        return sqlite3.connect(self.db_path)

    def enable_wal_mode(self):
        """Enable Write-Ahead Logging (WAL) mode to reduce locking issues."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            conn.commit()

    def db_login(self, email, password):
        """Check user login."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM tbl_users WHERE usr_email=? AND usr_pass=?"
            cursor.execute(query, (email, password))
            return "yes" if cursor.fetchone() else "no"

    def get_key_status(self):
        """Get encryption key and status."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "SELECT key_, status_ FROM face_encrypt"
            cursor.execute(query)
            return cursor.fetchone() or ("no", "no")

    def update_status(self, key, status_):
        """Update encryption key status."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE face_encrypt SET key_=?, status_=?", (key, status_))
            conn.commit()
            return "yes"

    def clear_all(self):
        """Delete all users from the table."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tbl_users")
            conn.commit()
            return "yes"

    def db_facial_login(self, user_id):
        """Fetch user details by user_id or if user_id exists in usr_ids column."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = """
            SELECT * FROM tbl_users 
            WHERE user_id = ? 
            OR instr(',' || usr_ids || ',', ',' || ? || ',') > 0
            """
            cursor.execute(query, (user_id, str(user_id)))
            result = cursor.fetchone()
            return (result[2], result[4], result[5]) if result else None

    def db_register(self, user_id, name, email, password, mobile, user_type, usr_ids):
        """Register a new user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = """
            INSERT INTO tbl_users (user_id, usr_name, usr_email, usr_mobile, usr_pass, usr_type, usr_ids)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (user_id, name, email, mobile, password, user_type, usr_ids))
            conn.commit()

    def get_users(self):
        """Fetch all users."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT usr_name, usr_email, usr_mobile, usr_type, usr_pass FROM tbl_users"
            cursor.execute(query)
            return cursor.fetchall()

    def db_create(self, tablename):
        """Create a table if it does not exist."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            CREATE TABLE IF NOT EXISTS {tablename} (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                _to TEXT NOT NULL,
                _from TEXT NOT NULL,
                _subject TEXT NOT NULL,
                _date TEXT NOT NULL,
                _DataFile TEXT NOT NULL,
                _FolderName TEXT NOT NULL
            )"""
            cursor.execute(query)

    def db_insert(self, _to, _from, _subject, _date, _dataFile, _folderName, tablename):
        """Insert a new record into the table using a single connection."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            INSERT INTO {tablename} (_to, _from, _subject, _date, _DataFile, _FolderName)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (_to, _from, _subject, _date, _dataFile, _folderName))
            conn.commit()

            if _folderName != "Drafts":
                self.db_drop_by_subject(_subject, conn)
                self.db_insert_receiver(_to, _from, _subject, _date, _dataFile, _folderName, tablename, conn)

    def db_insert_receiver(self, _to, _from, _subject, _date, _dataFile, _folderName, tablename, conn):
        """Insert email into receiver's inbox using the same connection."""
        cursor = conn.cursor()
        query = f"""
        INSERT INTO {tablename} (_to, _from, _subject, _date, _DataFile, _FolderName)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (_to, _from, _subject, _date, _dataFile, "Inbox"))
        self.db_drop_by_subject(_subject, conn)
        conn.commit()

    def db_read(self, tbl_name, folder_name, user):
        """Read emails from a folder for a user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT * FROM {tbl_name} 
            WHERE _FolderName = ? AND _from = ? 
            ORDER BY _date DESC
            """
            cursor.execute(query, (folder_name, user))
            return cursor.fetchall()

    def db_read_inbox(self, tbl_name, folder_name, user):
        """Read received emails for a user."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT * FROM {tbl_name} 
            WHERE _FolderName = ? AND _to = ? 
            ORDER BY _date DESC
            """
            cursor.execute(query, (folder_name, user))
            return cursor.fetchall()

    def db_read_by_id(self, tbl_name, record_id):
        """Fetch an email by ID."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {tbl_name} WHERE _id = ?"
            cursor.execute(query, (record_id,))
            return cursor.fetchall()

    def db_drop_by_subject(self, subject, conn):
        """Delete draft emails with a specific subject using the same connection."""
        cursor = conn.cursor()
        query = "DELETE FROM send_receive WHERE _FolderName = 'Drafts' AND _subject = ?"
        cursor.execute(query, (subject,))
        conn.commit()

    def log(self, user_id):
        """Log user activity by fetching details."""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = """
            SELECT * FROM tbl_users 
            WHERE user_id = ? 
            OR instr(',' || usr_ids || ',', ',' || ? || ',') > 0
            """
            cursor.execute(query, (user_id, str(user_id)))
            return cursor.fetchall() or None
