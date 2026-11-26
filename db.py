import hashlib
import secrets
import sqlite3
import time

DB_NAME = "reading_aid.db"


def _ensure_columns(cursor: sqlite3.Cursor) -> None:
    cursor.execute("PRAGMA table_info(profiles)")
    profile_cols = {row[1] for row in cursor.fetchall()}

    if "preferred_theme" not in profile_cols:
        cursor.execute("ALTER TABLE profiles ADD COLUMN preferred_theme TEXT DEFAULT 'Dark'")
    if "reduced_motion" not in profile_cols:
        cursor.execute("ALTER TABLE profiles ADD COLUMN reduced_motion BOOLEAN DEFAULT FALSE")
    if "celebration_effects" not in profile_cols:
        cursor.execute("ALTER TABLE profiles ADD COLUMN celebration_effects BOOLEAN DEFAULT TRUE")
    if "avatar_path" not in profile_cols:
        cursor.execute("ALTER TABLE profiles ADD COLUMN avatar_path TEXT DEFAULT ''")


def init_db() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'Student'
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                education_level TEXT,
                preferred_theme TEXT DEFAULT 'Dark',
                reduced_motion BOOLEAN DEFAULT FALSE,
                celebration_effects BOOLEAN DEFAULT TRUE,
                avatar_path TEXT DEFAULT '',
                FOREIGN KEY (username) REFERENCES users (username)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                expires_at REAL NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users (username)
            )
            """
        )
        _ensure_columns(cursor)
        conn.commit()


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, role: str = "Student") -> bool:
    init_db()
    password_hash = _hash_password(password)
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            cursor.execute(
                """
                INSERT INTO profiles (username, preferred_theme, reduced_motion, celebration_effects, avatar_path)
                VALUES (?, 'Dark', 0, 1, '')
                """,
                (username,),
            )
            cursor.execute(
                "INSERT INTO activity_log (username, description) VALUES (?, ?)",
                (username, "Registered account"),
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def authenticate_user(username: str, password: str):
    init_db()
    password_hash = _hash_password(password)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash),
        )
        user = cursor.fetchone()
        if user:
            log_activity(username, "Logged in")
        return user


def get_user_by_username(username: str):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        return cursor.fetchone()


def reset_password(username: str, new_password: str) -> bool:
    init_db()
    password_hash = _hash_password(new_password)
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE LOWER(username) = LOWER(?)",
                (password_hash, username),
            )
            if cursor.rowcount == 0:
                return False
            log_activity(username, "Reset password")
            conn.commit()
            return True
    except Exception:
        return False


def load_profile(username: str) -> dict:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE username = ?", (username,))
        row = cursor.fetchone()
        user_row = get_user_by_username(username)
        role_val = user_row[3] if user_row and len(user_row) > 3 else "Student"
        if row:
            return {
                "username": row[1],
                "full_name": row[2],
                "email": row[3],
                "education_level": row[4],
                "preferred_theme": row[5] or "Dark",
                "reduced_motion": bool(row[6]),
                "celebration_effects": bool(row[7]) if row[7] is not None else True,
                "avatar_path": row[8] if len(row) > 8 and row[8] else "",
                "role": role_val,
            }
        return {"role": role_val, "avatar_path": ""}


def update_profile(
    username: str,
    full_name: str,
    email: str,
    education_level: str,
    reduced_motion: bool = False,
    celebration_effects: bool = True,
    avatar_path: str | None = None,
) -> None:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if avatar_path is None:
            cursor.execute(
                """
                UPDATE profiles SET
                full_name = ?,
                email = ?,
                education_level = ?,
                reduced_motion = ?,
                celebration_effects = ?
                WHERE username = ?
                """,
                (
                    full_name,
                    email,
                    education_level,
                    reduced_motion,
                    celebration_effects,
                    username,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE profiles SET
                full_name = ?,
                email = ?,
                education_level = ?,
                reduced_motion = ?,
                celebration_effects = ?,
                avatar_path = ?
                WHERE username = ?
                """,
                (
                    full_name,
                    email,
                    education_level,
                    reduced_motion,
                    celebration_effects,
                    avatar_path,
                    username,
                ),
            )
        log_activity(username, "Updated profile")
        conn.commit()


def update_avatar_path(username: str, avatar_path: str) -> None:
    if not username:
        return
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE profiles SET avatar_path = ? WHERE username = ?",
            (avatar_path, username),
        )
        conn.commit()


def update_theme(username: str, theme: str) -> None:
    if not username:
        return
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE profiles SET preferred_theme = ? WHERE username = ?",
            (theme, username),
        )
        conn.commit()


def get_all_users() -> list:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()


def delete_user(user_id: int) -> None:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()


def log_activity(username: str, description: str) -> None:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_log (username, description) VALUES (?, ?)",
            (username, description),
        )
        conn.commit()


def get_all_activities() -> list:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC")
        return cursor.fetchall()


def create_session_token(username: str, role: str) -> str:
    init_db()
    token = secrets.token_hex(32)
    expires_at = time.time() + (24 * 60 * 60)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (username, token, role, expires_at) VALUES (?, ?, ?, ?)",
            (username, token, role, expires_at),
        )
        conn.commit()
    return token


def get_user_from_session_token(token: str):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sessions WHERE token = ? AND expires_at > ?",
            (token, time.time()),
        )
        session = cursor.fetchone()
        if session:
            username = session[1]
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()
        return None


def delete_session_token(token: str) -> None:
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()