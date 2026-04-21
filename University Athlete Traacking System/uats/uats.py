# LOGIN_CLI_UATS

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import getpass
from http.server import HTTPServer

MAX_ATTEMPTS = 3

@dataclass
class Session:
    is_logged_in: bool = False
    username: str | None = None
    attempts_left: int = MAX_ATTEMPTS

def log_event(message: str, logfile: str = "app.log") -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")

def prompt_credentials() -> tuple[str, str]:
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    return username, password

def login(session: Session, validate_fn) -> Session:
    if session.is_logged_in:
        print(f"Already logged in as {session.username}.")
        return session
    if session.attempts_left <= 0:
        print("No attempts left.")
        return session

    username, password = prompt_credentials()
    if validate_fn(username, password):
        session.is_logged_in = True
        session.username = username
        session.attempts_left = MAX_ATTEMPTS
        print(f"Login successful. Welcome, {username}!")
        log_event(f"LOGIN success user={username}")
    else:
        session.attempts_left -= 1
        print(f"Invalid credentials. Attempts left: {session.attempts_left}")
        log_event(f"LOGIN failed user={username} attempts_left={session.attempts_left}")
    return session

def logout(session: Session) -> Session:
    if not session.is_logged_in:
        print("You are not logged in.")
        return session
    user = session.username
    session.is_logged_in = False
    session.username = None
    print("Logged out.")
    log_event(f"LOGOUT user={user}")
    return session

def require_login(session: Session) -> bool:
    if not session.is_logged_in:
        print("Access denied. Please login first.")
        return False
    return True



import re


def restricted_action(session: Session):
    if not require_login(session):
        return
    print("Restricted action executed.")


def menu_loop(session: Session):
    while True:
        show_menu(session)
        choice = read_choice()

        # --- NOT LOGGED IN MENU ---
        if not session.is_logged_in:
            if choice == "1":
                session = login(session, validate_credentials_db)
                continue
            elif choice == "2":
                print("Bye!")
                return
            else:
                print("Invalid option.")
                continue

        # --- LOGGED IN MENU ---
        if choice == "1":
            athletes = get_all_athletes_db()
            print("\n--- ATHLETES ---")
            for a in athletes:
                print(a)
            input("\nPress Enter...")
            continue

        elif choice == "2":
            # -------- NAME --------
            while True:
                name = input("Name of Athlete_uats: ").strip()
                if re.fullmatch(r"[A-Za-z\s\-]+", name):
                    break
                print("❌ Name must contain only English letters (A–Z). Try again.")

            # -------- BIRTHDATE (18–100) --------
            while True:
                birthdate = input("Birthdate_uats (YYYY-MM-DD): ").strip()
                try:
                    dob = datetime.strptime(birthdate, "%Y-%m-%d").date()
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    if 18 <= age <= 100:
                        break
                    print("❌ Age must be between 18 and 100. Try again.")
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD. Try again.")

            # -------- GENDER (M/F) --------
            while True:
                gender = input("Gender_uats (M/F): ").strip().upper()
                if gender in ("M", "F"):
                    break
                print("❌ Enter M or F only.")

            faculty = input("Faculty_uats: ").strip()
            sports = input("Sport_uats: ").strip()

            # -------- EMAIL --------
            while True:
                email = input("Email_uats: ").strip()
                if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
                    break
                print("❌ Invalid email format.")

            # -------- GPA (0; 5] --------
            while True:
                gpa_str = input("GPA_uats (0 - 5.00]: ").strip().replace(",", ".")
                try:
                    gpa_val = float(gpa_str)
                    if 0 < gpa_val <= 5:
                       gpa = f"{gpa_val:.2f}"
                       break
                    print("❌ GPA must be greater than 0 and less than or equal to 5. Try again.")
                except ValueError:
                    print("❌ GPA must be a number (example: 3.75). Try again.")

            create_athlete_db(name, birthdate, gender, faculty, sports, email, gpa)
            print("Athlete added.")
            input("\nPress Enter...")
            continue

        elif choice == "3":
            aid = input("Athlete ID: ").strip()
            athlete = get_athlete_by_id_db(aid)
            if athlete is None:
                print("Athlete not found.")
            else:
                print(athlete)
            input("\nPress Enter...")
            continue

        elif choice == "4":
            aid = input("Athlete ID: ").strip()
            old = get_athlete_by_id_db(aid)
            if old is None:
                print("Athlete not found.")
                input("\nPress Enter...")
                continue

            print(f"Current: {old}")

            name = input("New Name_uats: ").strip()
            birthdate = input("New Birthdate_uats (YYYY-MM-DD): ").strip()

            while True:
                gender = input("New Gender_uats (M/F): ").strip().upper()
                if gender in ("M", "F"):
                    break
                print("❌ Enter M or F only.")

            faculty = input("New Faculty_uats: ").strip()
            sports = input("New Sport_uats: ").strip()

            while True:
                email = input("New Email_uats: ").strip()
                if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
                    break
                print("❌ Invalid email format.")

            while True:
                gpa_str = input("New GPA_uats (0.01 - 5.00): ").strip().replace(",", ".")
                try:
                    gpa_val = float(gpa_str)
                    if 0.01 <= gpa_val <= 5.00:
                        gpa = f"{gpa_val:.2f}"
                        break
                    print("❌ GPA must be between 0.01 and 5.00. Try again.")
                except ValueError:
                    print("❌ GPA must be a number (example: 3.75). Try again.")

            updated = update_athlete_db(aid, name, birthdate, gender, faculty, sports, email, gpa)
            if updated == 0:
                print("Nothing updated (wrong ID?).")
            else:
                print("Athlete updated.")
            input("\nPress Enter...")
            continue

        elif choice == "5":
            aid = input("Athlete ID to delete: ").strip()
            deleted = delete_athlete_db(aid)

            if deleted == 0:
                print("Nothing deleted (wrong ID?).")
            else:
                print("Athlete deleted.")
            input("\nPress Enter...")
            continue

        elif choice == "6":
            print("\n--- ADD ADMIN USER ---")

            while True:
                username = input("Username_uats: ").strip()
                if re.fullmatch(r"[A-Za-z0-9_.-]+", username):
                    break
                print("❌ Username must contain only Latin letters, digits, and _ . -")

            while True:
                password = input("Password_uats: ").strip()

                if len(password) < 4:
                    print("❌ Password must be at least 4 characters.")
                    continue
                if not re.search(r"[A-Za-z]", password):
                    print("❌ Password must contain at least 1 letter (A–Z).")
                    continue
                if not re.search(r"[0-9]", password):
                    print("❌ Password must contain at least 1 number (0–9).")
                    continue
                if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>?/\\|`~]", password):
                    print("❌ Password must contain at least 1 special character (! @ # $ etc).")
                    continue

                break

            while True:
                full_name = input("Full_name_uats: ").strip()
                if re.fullmatch(r"[A-Za-z\s\-]+", full_name):
                    break
                print("❌ Full name must contain only English letters (A-Z). Try again.")

            activity = input("Activity_uats: ").strip()

            new_id = create_user_db(username, password, full_name, activity)
            print(f"User created with id: {new_id}")
            input("\nPress Enter...")
            continue

        elif choice == "7":
            print("\n--- MODIFY HEADER DATA ---")
            system = input("System name: ").strip()

            updated = update_header_db(system)
            print("Header updated." if updated else "Nothing updated.")
            input("\nPress Enter...")
            continue

        elif choice == "8":
            print("\n--- MODIFY FOOTER DATA ---")
            old = get_footer_db()
            print("Current footer:", old)

            system_name = input("System name: ").strip()
            contact_email = input("Contact email: ").strip()
            year = input("Year: ").strip()
            contact_phone = input("Contact phone: ").strip()

            updated = update_footer_db(system_name, contact_email, year, contact_phone)

            if updated == 0:
                print("Nothing updated.")
            else:
                print("Footer updated successfully.")

            input("\nPress Enter...")
            continue

        elif choice == "9":
            session = logout(session)
            continue

        elif choice == "10":
            print("Bye!")
            return

        else:
            print("Invalid option.")
            continue
        


# --- MAIN EXECUTION BLOCK ---










# DB_CLI_UATS


import mysql.connector

# NOTE:
# Update UATS_USER and UATS_PASSWORD to match your local MySQL credentials.
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "uats"

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def validate_credentials_db(username_uats: str, password_uats: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM users_uats WHERE username_uats=%s AND password_uats=%s LIMIT 1",
            (username_uats, password_uats)
        )
        return cur.fetchone() is not None
    finally:
        conn.close()

# =========================
# ATHLETES CRUD
# =========================

def create_athlete_db(athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats, gpa_uats):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO athletes_uats
            (athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats, gpa_uats)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            athlete_name_uats,
            birthdate_uats,
            gender_uats,
            faculty_uats,
            sports_uats,
            email_uats,
            gpa_uats
        ))
        conn.commit()
    finally:
        conn.close()


def get_all_athletes_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT athlete_id_uats, athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats,gpa_uats
            FROM athletes_uats
        """)
        return cur.fetchall()
    finally:
        conn.close()

def get_athlete_by_id_db(athlete_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT athlete_id_uats, athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats,gpa_uats
            FROM athletes_uats
            WHERE athlete_id_uats = %s
            LIMIT 1
        """, (athlete_id,))
        return cur.fetchone()
    finally:
        conn.close()

def update_athlete_db(athlete_id_uats, athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats, gpa_uats):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE athletes_uats
            SET athlete_name_uats = %s,
                birthdate_uats = %s,
                gender_uats = %s,
                faculty_uats = %s,
                sports_uats = %s,
                email_uats = %s,
                gpa_uats = %s
            WHERE athlete_id_uats = %s
        """, (athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats, gpa_uats, athlete_id_uats))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def delete_athlete_db(athlete_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM athletes_uats WHERE athlete_id_uats = %s", (athlete_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

# =========================
# SYSTEM DATA (Header/Footer)
# =========================

def get_footer_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT copyright_text_uats, contact_email_uats, year_uats
            FROM Footer_table_uats
            LIMIT 1
        """)
        return cur.fetchone()
    finally:
        conn.close()

def get_header_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT System_name_uats
            FROM Header_table_uats
            LIMIT 1
        """)
        return cur.fetchone()
    finally:
        conn.close()

def create_user_db(username_uats: str, password_uats: str, full_name_uats: str, activity_uats: str) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users_uats (username_uats, password_uats, full_name_uats, activity_uats)
            VALUES (%s, %s, %s, %s)
        """, (username_uats, password_uats, full_name_uats, activity_uats))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
def update_header_db(system_name: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE Header_table_uats
            SET System_name_uats = %s
            WHERE Header_id_uats = 1
        """, (system_name,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def get_footer_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT footer_id_uats, system_name_uats,
                   contact_email_uats, year_uats, contact_phone_uats
            FROM Footer_table_uats
            ORDER BY footer_id_uats ASC
            LIMIT 1
        """)
        return cur.fetchone()
    finally:
        conn.close()

def update_footer_db(system_name, contact_email, year, contact_phone):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE Footer_table_uats
            SET system_name_uats = %s,
                contact_email_uats = %s,
                year_uats = %s,
                contact_phone_uats = %s
            WHERE footer_id_uats = 1
        """, (system_name, contact_email, year, contact_phone))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()



        # MENU_CLI_UATS

    from auth_uats import Session


def show_menu(session: Session) -> None:
    print("\n===============================")
    print(" University Athlete Tracking System (UATS) ")
    print("===============================")

    if session.is_logged_in:
        print(f"Logged in as: {session.username}")
        print("1. List Athletes ")
        print("2. Add Athlete ")
        print("3. Load Athlete by ID")
        print("4. Update Athlete ")
        print("5. Delete Athlete ")
        print("6. Add new user with admin rights")
        print("7. Modify Header Data")
        print("8. Update Footer Data")
        print("9. Logout")
        print("10. Exit")
    else:
        print("Not logged in")
        print("1. Login")
        print("2. Exit")


def read_choice() -> str:
    return input("Select option: ").strip()    





#LOGIN_SIGNUP_PAGE_FRONTEND_UATS


import http.server
import socketserver
import mysql.connector
from mysql.connector import errorcode
import os
import sys
import re
import json
import base64
import secrets
import hashlib
import time
import html
from urllib.parse import parse_qs, urlparse, quote
from datetime import datetime, date
from http import cookies

# =================================================================================================
# SECTION 1: CONFIGURATION AND CONSTANTS 
# =================================================================================================

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "uats"
SERVER_PORT = 8080

LOGO_FILENAME = "logo_uats.png"
DEFAULT_CONTENT_TYPE = "text/html; charset=utf-8"

ACTIVE_SESSIONS = {}

REGEX_ENGLISH_ONLY = r"^[a-zA-Z0-9\s.,!?'\"()\-]*$"
REGEX_PASSWORD = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{4,}$"
def is_english_only(text):
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False
    
REGEX_EMAIL = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
REGEX_FULLNAME = r"^[A-Za-z\s]+$"



# =================================================================================================
# SECTION 2: DATABASE LAYER 
# =================================================================================================

class DatabaseManager:
    @staticmethod
    def get_connection():
        try:
            return mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=True
            )
        except mysql.connector.Error as err:
            return None

    @staticmethod
    def validate_credentials_db(username_uats: str, password_uats: str):
        conn = DatabaseManager.get_connection()
        if not conn: return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT user_id_uats, username_uats, full_name_uats, activity_uats "
                "FROM users_uats WHERE username_uats=%s AND password_uats=%s LIMIT 1",
                (username_uats, password_uats)
            )
            return cur.fetchone()
        except mysql.connector.Error:
            return None
        finally:
            if conn: conn.close()

    @staticmethod
    def create_user_db(username_uats: str, password_uats: str, full_name_uats: str, activity_uats: str) -> int:
        conn = DatabaseManager.get_connection()
        if not conn: return -1
        try:
            cur = conn.cursor()
            cur.execute("""
                        INSERT INTO users_uats (username_uats, password_uats, full_name_uats, activity_uats)
                        VALUES (%s, %s, %s, %s)
                        """, (username_uats, password_uats, full_name_uats, activity_uats))
            conn.commit()
            return cur.lastrowid
        except mysql.connector.Error as err:
            raise err
        finally:
            if conn: conn.close()

    @staticmethod
    def create_athlete_db(athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats,
                          gpa_uats):
        conn = DatabaseManager.get_connection()
        if not conn: return False
        try:
            cur = conn.cursor()
            cur.execute("SELECT MAX(athlete_id_uats) FROM athletes_uats")
            row = cur.fetchone()
            next_id = 1
            if row and row[0]:
                next_id = int(row[0]) + 1

            cur.execute("""
                        INSERT INTO athletes_uats
                        (athlete_id_uats, athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats,
                         email_uats, gpa_uats)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (next_id, athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats,
                         gpa_uats))
            conn.commit()
            return True
        except mysql.connector.Error:
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_all_athletes_db():
        conn = DatabaseManager.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            cur.execute("""
                        SELECT athlete_id_uats,
                               athlete_name_uats,
                               birthdate_uats,
                               gender_uats,
                               faculty_uats,
                               sports_uats,
                               email_uats,
                               gpa_uats
                        FROM athletes_uats
                        """)
            return cur.fetchall()
        except mysql.connector.Error:
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def get_athlete_by_id_db(athlete_id):
        conn = DatabaseManager.get_connection()
        if not conn: return None
        try:
            cur = conn.cursor()
            cur.execute("""
                        SELECT athlete_id_uats,
                               athlete_name_uats,
                               birthdate_uats,
                               gender_uats,
                               faculty_uats,
                               sports_uats,
                               email_uats,
                               gpa_uats
                        FROM athletes_uats
                        WHERE athlete_id_uats = %s LIMIT 1
                        """, (athlete_id,))
            return cur.fetchone()
        except mysql.connector.Error:
            return None
        finally:
            if conn: conn.close()

    @staticmethod
    def update_athlete_db(athlete_id_uats, athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats,
                          email_uats, gpa_uats):
        conn = DatabaseManager.get_connection()
        if not conn: return 0
        try:
            cur = conn.cursor()
            cur.execute("""
                        UPDATE athletes_uats
                        SET athlete_name_uats = %s,
                            birthdate_uats    = %s,
                            gender_uats       = %s,
                            faculty_uats      = %s,
                            sports_uats       = %s,
                            email_uats        = %s,
                            gpa_uats          = %s
                        WHERE athlete_id_uats = %s
                        """, (athlete_name_uats, birthdate_uats, gender_uats, faculty_uats, sports_uats, email_uats,
                              gpa_uats, athlete_id_uats))
            conn.commit()
            return cur.rowcount
        except mysql.connector.Error:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def delete_athlete_db(athlete_id):
        conn = DatabaseManager.get_connection()
        if not conn: return 0
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM athletes_uats WHERE athlete_id_uats = %s", (athlete_id,))
            conn.commit()
            return cur.rowcount
        except mysql.connector.Error:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def get_header_db():
        conn = DatabaseManager.get_connection()
        if not conn: return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT Header_id_uats, System_name_uats, Logo_uats FROM Header_table_uats LIMIT 1")
            return cur.fetchone()
        except mysql.connector.Error:
            return None
        finally:
            if conn: conn.close()

    @staticmethod
    def update_header_db(header_id, system_name, logo_content=None):
        conn = DatabaseManager.get_connection()
        if not conn: return 0
        try:
            cur = conn.cursor()
            if logo_content:
                cur.execute(
                    "UPDATE Header_table_uats SET System_name_uats = %s, Logo_uats = %s WHERE Header_id_uats = %s",
                    (system_name, logo_content, header_id))
            else:
                cur.execute("UPDATE Header_table_uats SET System_name_uats = %s WHERE Header_id_uats = %s",
                            (system_name, header_id))
            conn.commit()
            return cur.rowcount
        except mysql.connector.Error:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def get_footer_db():
        conn = DatabaseManager.get_connection()
        if not conn: return None
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT footer_id_uats, system_name_uats, contact_email_uats, year_uats, contact_phone_uats FROM Footer_table_uats LIMIT 1")
            return cur.fetchone()
        except mysql.connector.Error:
            return None
        finally:
            if conn: conn.close()

    @staticmethod
    def update_footer_db(footer_id, system_name, contact_email, year, contact_phone):
        conn = DatabaseManager.get_connection()
        if not conn: return 0
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE Footer_table_uats SET system_name_uats = %s, contact_email_uats = %s, year_uats = %s, contact_phone_uats = %s WHERE footer_id_uats = %s",
                (system_name, contact_email, year, contact_phone, footer_id))
            conn.commit()
            return cur.rowcount
        except mysql.connector.Error:
            return 0
        finally:
            if conn: conn.close()


# =================================================================================================
# SECTION 3: FRONTEND STYLING & AUTHENTICATION PAGES (GLOWING UI) 
# =================================================================================================

def render_head_styles():
    return r"""
<style>
.shimmer{
  position:absolute; inset:0;
  background: radial-gradient(circle at 20% 20%, rgba(235,212,105,0.10), transparent 55%),
              radial-gradient(circle at 80% 70%, rgba(123,63,176,0.14), transparent 60%);
  animation: shimmerMove 10s ease-in-out infinite alternate;
  opacity: 0.9;
  pointer-events:none;
}
@keyframes shimmerMove{
  from{ transform: translate(0,0) scale(1); }
  to  { transform: translate(-18px,12px) scale(1.05); }
}

.noise{
  position:absolute; inset:0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='.25'/%3E%3C/svg%3E");
  opacity: 0.08;
  mix-blend-mode: overlay;
  pointer-events:none;
}

  :root {
    --black: #09090c;
    --purple-dark: #1a0b2e;
    --purple: #3a155a;
    --purple-glow: #7b3fb0;
    --silver: #cfcfcf;
    --border: rgba(255,255,255,0.12);
    --gold: #ebd469;

    --success-bg: rgba(12, 78, 36, 0.35);
    --success-border: rgba(34, 197, 94, 0.5);
    --error-bg: rgba(92, 18, 18, 0.35);
    --error-border: rgba(239, 68, 68, 0.55);
  }

  * { box-sizing: border-box; font-family: "Goldman", system-ui, sans-serif; }

  body { margin: 0; min-height: 100vh; overflow: auto; color: var(--silver); background: var(--black); }

  .ambient { position: fixed; inset: 0; z-index: -1; overflow: hidden; }

  .particles { position: absolute; inset: 0; pointer-events: none; opacity: 0.55; }
  .particle { position: absolute; width: 2px; height: 2px; border-radius: 999px; background: rgba(123,63,176,0.45); filter: blur(0.2px); animation: pFloat linear infinite; }

  @keyframes pFloat {
    from { transform: translateY(30px); opacity: 0; }
    15%  { opacity: 0.45; }
    85%  { opacity: 0.45; }
    to   { transform: translateY(-140px); opacity: 0; }
  }

  .blob {
    position: absolute; width: 420px; height: 420px;
    background: radial-gradient(circle, var(--purple-glow), transparent 65%);
    filter: blur(90px); opacity: 0.6; animation: float 28s infinite alternate ease-in-out;
  }
  .blob:nth-child(1) { top: -120px; left: -120px; animation-duration: 32s; }
  .blob:nth-child(2) { bottom: -140px; right: -120px; animation-duration: 36s; animation-delay: -8s; }
  .blob:nth-child(3) { top: 40%; left: 60%; width: 520px; height: 520px; animation-duration: 40s; animation-delay: -16s; }
  @keyframes float { from { transform: translate(0,0) scale(1); } to { transform: translate(-120px,80px) scale(1.2); } }

  .wrapper { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 18px; }

  .card {
    width: 100%; max-width: 440px; padding: 32px; border-radius: 20px;
    background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(0,0,0,0.7));
    border: 1px solid var(--border); backdrop-filter: blur(10px);
    box-shadow: 0 30px 60px rgba(0,0,0,0.7);
    transition: box-shadow 0.35s ease, transform 0.35s ease, border-color 0.35s ease;
  }
  .card:hover {
    border-color: rgba(123,63,176,0.35);
    box-shadow: 0 35px 70px rgba(0,0,0,0.75), 0 0 45px rgba(123,63,176,0.25);
    transform: translateY(-2px);
  }

  .logo { width: 280px; height: 280px; margin: 0 auto 18px; border-radius: 18px; overflow: hidden; background: transparent; box-shadow: 0 15px 40px rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; }
  .logo img { width: 100%; height: 100%; object-fit: contain; display: block; }
  h1 { text-align:center; margin: 0; font-size: 22px; letter-spacing: 1px; color: #f2f2f2; }
  p  { text-align:center; font-size: 13px; color: #b0b0b0; margin-bottom: 22px; }
  label { display:block; font-size: 13px; margin: 14px 0 6px; }

  input { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid var(--border); background: rgba(0,0,0,0.6); color: var(--silver); outline: none; transition: border-color 0.25s ease, box-shadow 0.25s ease; }
  input:focus { border-color: var(--purple-glow); box-shadow: 0 0 0 3px rgba(123,63,176,0.25); }

  button {
    margin-top: 18px; width: 100%; padding: 12px; border-radius: 14px; border: none; cursor: pointer;
    font-weight: 700; letter-spacing: 1px; color: #eee;
    background: linear-gradient(135deg, var(--purple), var(--purple-dark));
    position: relative; overflow: hidden; isolation: isolate; animation: breathe 4.5s ease-in-out infinite;
  }
  button:hover { filter: brightness(1.1); }
  button::before {
    content: ""; position: absolute; inset: -2px; border-radius: inherit;
    background: linear-gradient(120deg, transparent, rgba(123,63,176,0.9), rgba(235,212,105,0.9), rgba(123,63,176,0.9), transparent);
    background-size: 300% 300%; animation: glowMove 6s linear infinite; opacity: 0.85; z-index: -1;
  }
  button::after { content: ""; position: absolute; inset: 1px; background: linear-gradient(135deg, var(--purple), var(--purple-dark)); border-radius: inherit; z-index: -1; }
  @keyframes glowMove { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
  @keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.02); } }
  button:hover::before { opacity: 1; filter: blur(1px); }

  .msg { display: none; margin-top: 14px; padding: 10px; border-radius: 12px; font-size: 14px; font-weight: bold; text-align: center; border: 1px solid transparent; }
  .msg.success { display: block; background: var(--success-bg); border-color: var(--success-border); color: #4caf50; }
  .msg.error   { display: block; background: var(--error-bg); border-color: var(--error-border); color: #f44336; }

  .hint { margin-top: 8px; font-size: 12px; color: #b0b0b0; line-height: 1.4; }
  .hint b { color: #e6e6e6; }
  .footer { margin-top: 18px; text-align: center; font-size: 12px; color: #8a8a8a; }
  .footer a { color: #cfcfcf; text-decoration: none; }
  .footer a:hover { text-decoration: underline; }

  .live { margin-top: 10px; font-size: 12px; color: #b0b0b0; text-align: left; padding: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.35); }
  .live .ok { color: #9ee6b8; }
  .live .bad { color: #ffb3b3; }
</style>
"""


def render_login_page(message_type="", message_text=""):
    msg_html = f"<div class='msg {message_type}'>{message_text}</div>" if message_text else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>University Athlete Tracking System</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link href="https://fonts.googleapis.com/css2?family=Goldman:wght@400;700&display=swap" rel="stylesheet">
  {render_head_styles()}
</head>
<body>
  <div class="ambient">
    <div class="shimmer"></div>
    <div class="blob"></div><div class="blob"></div><div class="blob"></div>
    <div class="noise"></div>
    <div class="particles">
      <span class="particle" style="left:10%; top:85%; animation-duration:10s;"></span>
      <span class="particle" style="left:22%; top:92%; animation-duration:12s;"></span>
      <span class="particle" style="left:35%; top:88%; animation-duration:14s;"></span>
      <span class="particle" style="left:50%; top:94%; animation-duration:11s;"></span>
      <span class="particle" style="left:66%; top:90%; animation-duration:13s;"></span>
      <span class="particle" style="left:78%; top:96%; animation-duration:9s;"></span>
      <span class="particle" style="left:90%; top:86%; animation-duration:15s;"></span>
    </div>
  </div>

  <div class="wrapper">
    <div class="card">
      <div class="logo"><img src="/logo.png" alt="UATS Logo"></div>
      <h1>University Athlete Tracking System (UATS)</h1>
      <p></p>
      <form method="POST" action="/">
        <label>Username_uats</label><input name="username" type="text" required />
        <label>Password_uats</label><input name="password" type="password" required />
        {msg_html}
        <button type="submit">SIGN IN</button>
      </form>
      <div class="footer">Don’t have an account? <a href="/register">Create account</a></div>
    </div>
  </div>
</body>
</html>
"""


def render_register_page(message_type="", message_text="", full_name_val="", activity_val="", username_val=""):
    msg_html = f"<div class='msg {message_type}'>{message_text}</div>" if message_text else ""
    hint_html = """
      <div class="hint">
        <b>Password rules:</b><br>
        • At least 4 characters<br>
        • At least 1 letter (A–Z)<br>
        • At least 1 number (0–9)<br>
        • At least 1 special character (example: ! @ # $)
      </div>
      <div id="liveBox" class="live" style="display:none;"></div>
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Create Account</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link href="https://fonts.googleapis.com/css2?family=Goldman:wght@400;700&display=swap" rel="stylesheet">
    {render_head_styles()}
</head>
<body>
<div class="ambient">
  <div class="shimmer"></div>
  <div class="blob"></div><div class="blob"></div><div class="blob"></div>
  <div class="noise"></div>
  <div class="particles">
    <span class="particle" style="left:10%; top:85%; animation-duration:10s;"></span>
    <span class="particle" style="left:22%; top:92%; animation-duration:12s;"></span>
    <span class="particle" style="left:35%; top:88%; animation-duration:14s;"></span>
    <span class="particle" style="left:50%; top:94%; animation-duration:11s;"></span>
    <span class="particle" style="left:66%; top:90%; animation-duration:13s;"></span>
    <span class="particle" style="left:78%; top:96%; animation-duration:9s;"></span>
    <span class="particle" style="left:90%; top:86%; animation-duration:15s;"></span>
  </div>
</div>
  <div class="wrapper">
    <div class="card">
      <div class="logo"><img src="/logo.png" alt="UATS Logo"></div>
      <h1>Create Account</h1>
      <p>Register for UATS</p>
      <form method="POST" action="/register">
        <label>Full name</label><input name="full_name" type="text" required value="{full_name_val}" />
        <label>Activity (sport)</label><input name="activity" type="text" required value="{activity_val}" />
        <label>Username</label><input name="username" type="text" required value="{username_val}" />
        <label>Password</label><input id="pw" name="password" type="password" required />
        {hint_html}
        <label>Confirm password</label><input id="pw2" name="confirm" type="password" required />
        {msg_html}
        <button type="submit">REGISTER</button>
      </form>
      <div class="footer">Already have an account? <a href="/">Back to login</a></div>
    </div>
  </div>
<script>
  const pw = document.getElementById("pw");
  const liveBox = document.getElementById("liveBox");
  function hasLetter(s) {{ return /[A-Za-z]/.test(s); }}
  function hasNumber(s) {{ return /\\d/.test(s); }}
  function hasSpecial(s) {{ return /[!@#$%^&*()_+=\\-[\\]{{}};:,.<>?/\\\\|~`"']/.test(s); }}
  function updateLive() {{
    const v = pw.value || "";
    if (!v) {{ liveBox.style.display = "none"; return; }}
    liveBox.style.display = "block";
    const checks = [
      [v.length >= 4, "At least 4 characters"],
      [hasLetter(v), "At least 1 letter (A–Z)"],
      [hasNumber(v), "At least 1 number (0–9)"],
      [hasSpecial(v), "At least 1 special character (! @ # $ etc.)"]
    ];
    let html = "<b>Password check:</b><br>";
    for (const [ok, text] of checks) {{
      html += (ok ? "<span class='ok'>✓</span> " : "<span class='bad'>✗</span> ") + text + "<br>";
    }}
    liveBox.innerHTML = html;
  }}
  pw.addEventListener("input", updateLive);
</script>
</body>
</html>
"""


# =================================================================================================
# SECTION 4: DASHBOARD FRONTEND STYLING 
# =================================================================================================

class FrontendAssets:
    CSS_MAIN = """
    <link href="https://fonts.googleapis.com/css2?family=Goldman:wght@400;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --purple-dark: #0a0412; --purple-mid: #140826; --purple-glow: #7b3fb0; --yellow-main: #ebd469; --btn-purple: #7b44bf; --success-green: #4caf50; --error-red: #f44336; --text-silver: #cfcfcf; }
        body { font-family: 'Inter', sans-serif; margin: 0; padding: 20px; background: radial-gradient(circle at 50% 50%, var(--purple-mid) 0%, var(--purple-dark) 100%); background-attachment: fixed; min-height: 100vh; color: #e0e0e0; display: flex; flex-direction: column; }
        .uats-logo, .section-title, th, .btn-nav, h1 { font-family: 'Goldman', cursive; text-transform: uppercase; }
        .glass-card { background: rgba(20, 8, 38, 0.4); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; margin: 20px auto; width: 100%; max-width: 1400px; box-sizing: border-box; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); }
        .section-title { color: var(--yellow-main); font-size: 1.1em; margin-bottom: 20px; border-left: 4px solid var(--purple-glow); padding-left: 10px; letter-spacing: 1px; }
        .btn-nav { background: var(--yellow-main); color: var(--purple-dark); padding: 8px 16px; border-radius: 6px; font-weight: bold; border: none; cursor: pointer; font-size: 11px; text-decoration: none; display: inline-block; transition: filter 0.2s ease; }
        .btn-nav:hover { filter: brightness(1.1); }
        .btn-purple { background: var(--btn-purple); color: white; }
        .btn-danger { background: #c44d4d; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { text-align: left; color: var(--yellow-main); font-size: 13px; padding: 12px 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        td { padding: 14px 10px; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 15px; color: var(--text-silver); }
        .col-gpa { color: var(--yellow-main); font-weight: 700; text-align: right; }
        tr:hover td { background: rgba(255,255,255,0.02); }
        input, select { width: 100%; padding: 10px; background: rgba(0, 0, 0, 0.3); border: 1px solid var(--purple-glow); color: white; border-radius: 6px; outline: none; font-size: 14px; box-sizing: border-box; transition: border-color 0.3s; }
        /* HIDE DEFAULT DATE PICKER ICON because we use custom logic */
        input[type="date"]::-webkit-calendar-picker-indicator {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }
        input:focus { border-color: var(--yellow-main); }
        .field-row { display: flex; column-gap: 15px; row-gap: 35px; align-items: flex-start; flex-wrap: wrap; }
        .field-group { flex: 1; min-width: 140px; }
        label { font-size: 12px; margin-bottom: 6px; display: block; color: #aaa; font-weight: 600; letter-spacing: 0.5px;}
        .header-bar { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; margin-bottom: 10px; max-width: 1400px; margin-left: auto; margin-right: auto; width: 100%; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .header-logo { width: 80px; height: 80px; object-fit: contain; border-radius: 6px; background: rgba(255, 255, 255, 0.05); padding: 4px; }
        .message-box { padding: 12px 30px; margin: 10px auto 10px 0; border-radius: 8px; max-width: 400px; width: fit-content; text-align: left; font-weight: bold; font-size: 14px; box-sizing: border-box; }
        .welcome-section strong { color: var(--yellow-main); }
        .message-box { padding: 12px 30px; margin: 10px auto; border-radius: 8px; max-width: 400px; width: fit-content; text-align: center; font-weight: bold; font-size: 14px; box-sizing: border-box; }
        .msg-success { background-color: rgba(76, 175, 80, 0.15); border: 1px solid var(--success-green); color: var(--success-green); box-shadow: 0 0 10px rgba(76,175,80,0.1); }
        .msg-error { background-color: rgba(244, 67, 54, 0.15); border: 1px solid var(--error-red); color: var(--error-red); box-shadow: 0 0 10px rgba(244,67,54,0.1); }
        footer { margin-top: auto; padding: 40px 20px; background: rgba(10, 4, 18, 0.6); border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; width: 100%; box-sizing: border-box; }
        .footer-content { max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 8px; }
        .footer-copy { font-size: 14px; color: var(--yellow-main); font-family: 'Goldman'; letter-spacing: 1px; }
        .footer-info { font-size: 12px; color: #666; }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(8px); display: none; align-items: center; justify-content: center; z-index: 9999; }
        .modal-box { max-width: 400px; width: 90%; background: linear-gradient(135deg, rgba(20, 8, 38, 0.95), rgba(10, 4, 18, 0.98)); border: 1px solid var(--purple-glow); box-shadow: 0 0 30px rgba(123, 63, 176, 0.4); border-radius: 16px; padding: 30px; text-align: center; animation: modalPop 0.3s ease-out; }
        @keyframes modalPop { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        .inline-error { color: #f44336; font-size: 12px; margin-top:6px; }
    </style>
    """

    CSS_ANIMATIONS = """
    <style>
        .ambient{ position:fixed; inset:0; z-index:-1; overflow:hidden; }
        .shimmer{ position:absolute; inset:0; background: radial-gradient(circle at 20% 20%, rgba(235,212,105,0.05), transparent 55%), radial-gradient(circle at 80% 70%, rgba(123,63,176,0.08), transparent 60%); animation: shimmerMove 10s ease-in-out infinite alternate; opacity:.9; pointer-events:none; }
        @keyframes shimmerMove{ from{ transform: translate(0,0) scale(1); } to{ transform: translate(-18px,12px) scale(1.05); } }
        .particles{ position:absolute; inset:0; pointer-events:none; opacity:.55; }
        .particle{ position:absolute; width:2px; height:2px; border-radius:999px; background: rgba(123,63,176,0.45); filter: blur(.2px); animation: pFloat linear infinite; }
        @keyframes pFloat{ from{ transform: translateY(30px); opacity:0; } 15%{ opacity:.45; } 85%{ opacity:.45; } to{ transform: translateY(-140px); opacity:0; } }
    </style>
    """


# =================================================================================================
# SECTION 5: SERVER HANDLER & CONTROLLER 
# =================================================================================================

class UATSServerHandler(http.server.BaseHTTPRequestHandler):

    def _get_cookies(self):
        if "Cookie" in self.headers:
            return cookies.SimpleCookie(self.headers["Cookie"])
        return cookies.SimpleCookie()

    def _get_session(self):
        c = self._get_cookies()
        if "uats_session" in c:
            token = c["uats_session"].value
            if token in ACTIVE_SESSIONS:
                return ACTIVE_SESSIONS[token]
        return None

    def _set_session(self, user_row):
        token = secrets.token_urlsafe(32)
        ACTIVE_SESSIONS[token] = {
            "user_id": user_row['user_id_uats'],
            "username": user_row['username_uats'],
            "full_name": user_row['full_name_uats'],
            "login_time": time.time()
        }
        c = cookies.SimpleCookie()
        c["uats_session"] = token
        c["uats_session"]["path"] = "/"
        c["uats_session"]["httponly"] = True
        self.send_header("Set-Cookie", c.output(header="").strip())

    def _clear_session(self):
        c = self._get_cookies()
        if "uats_session" in c:
            token = c["uats_session"].value
            if token in ACTIVE_SESSIONS:
                del ACTIVE_SESSIONS[token]
        c = cookies.SimpleCookie()
        c["uats_session"] = ""
        c["uats_session"]["path"] = "/"
        c["uats_session"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        self.send_header("Set-Cookie", c.output(header="").strip())

    def _redirect(self, path, msg_key=None, msg_val=None):
        self.send_response(302)
        target = path
        if msg_key:
            sep = "&" if "?" in path else "?"
            # URL encode the message so spaces don't break the browser redirect
            target = f"{path}{sep}{msg_key}={quote(msg_val)}"
        self.send_header("Location", target)
        self.end_headers()

    def _send_html(self, content):
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except (ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception as e:
            print("Unexpected send error:", e)

    def _parse_multipart(self, data):
        content_type = self.headers.get('Content-Type', '')
        if "boundary=" not in content_type:
            return {}
        boundary = content_type.split("boundary=")[1].strip()
        if boundary.startswith('"') and boundary.endswith('"'):
            boundary = boundary[1:-1]
        boundary_bytes = ("--" + boundary).encode()
        parts = data.split(boundary_bytes)
        form_fields = {}
        for part in parts:
            if not part or part in (b"--\r\n", b"--"):
                continue
            if part.startswith(b"\r\n"):
                part = part[2:]
            if b"\r\n\r\n" not in part:
                continue
            headers_raw, body = part.split(b"\r\n\r\n", 1)
            body = body.rstrip(b"\r\n")
            headers = headers_raw.decode('utf-8', errors='ignore')
            name_match = re.search(r'name="([^"]+)"', headers)
            if not name_match:
                continue
            field_name = name_match.group(1)
            filename_match = re.search(r'filename="([^"]*)"', headers)
            if filename_match:
                filename = filename_match.group(1)
                if filename == "":
                    form_fields[field_name] = {'filename': '', 'content': b''}
                else:
                    form_fields[field_name] = {'filename': filename, 'content': body}
            else:
                form_fields[field_name] = body.decode('utf-8', errors='ignore')
        return form_fields

    def do_GET(self):

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == "/logo.png":
            header_data = DatabaseManager.get_header_db()
            if header_data and header_data[2]:
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(header_data[2])
            elif os.path.exists(LOGO_FILENAME):
                with open(LOGO_FILENAME, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Logo not found")
            return

        session = self._get_session()

        if path == "/" or path == "/login":
            if session:
                self._redirect("/dashboard")
            else:
                msg_text = "Wrong credentials" if "err" in query else ("Registration successful"
                                                                       " Please login") if "registered" in query else "Logout successful" if "logout" in query else ""
                msg_type = "success" if "registered" in query or "logout" in query else "error"
                self._send_html(render_login_page(msg_type, msg_text))
            return

        if path == "/register":
            msg_text = query.get("msg", [""])[0]
            self._send_html(render_register_page('error', msg_text))
            return

        if not session:
            self._redirect("/")
            return

        if path == "/dashboard":
            self.render_dashboard(query)
            return

        if path == "/load":
            aid = query.get("athlete_id_uats", [""])[0]
            if not aid:
                self._redirect("/dashboard", "msg", "Wrong: Please enter an ID to load")
                return
            athlete = DatabaseManager.get_athlete_by_id_db(aid)
            if athlete:
                self.render_dashboard(query, load_data=athlete, msg=(f"Load successful for ID {aid}", "success"))
            else:
                self._redirect("/dashboard", "msg", "Athlete ID not found.")
            return

        self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        content_len = int(self.headers.get('Content-Length', 0))

        if "multipart/form-data" in self.headers.get('Content-Type', ''):
            data = self.rfile.read(content_len)
            fields = self._parse_multipart(data)
        else:
            post_body = self.rfile.read(content_len).decode('utf-8')
            raw_fields = parse_qs(post_body)
            fields = {k: v[0] for k, v in raw_fields.items()}

        if path == "/":
            u = fields.get("username", "")
            p = fields.get("password", "")
            user = DatabaseManager.validate_credentials_db(u, p)
            if user:
                self.send_response(302)
                self._set_session(user)
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else:
                self._redirect("/?err=1")
            return

        if path == "/register":
            u = fields.get("username", "")
            p = fields.get("password", "")
            pc = fields.get("confirm", "")
            fn = fields.get("full_name", "")
            act = fields.get("activity", "")
            # English-only validation
            for field_name, value in [
                ("Full Name", fn),
                ("Activity", act),
                ("Username", u)
            ]:
                if not is_english_only(value):
                    self._send_html(render_register_page(
                        message_type="error",
                        message_text=f"{field_name} must use English characters only.",
                        full_name_val=html.escape(fn),
                        activity_val=html.escape(act),
                        username_val=html.escape(u)
                    ))
                    return

            if p != pc: self._redirect("/register", "msg", "Wrong: Passwords do not match."); return
            if not re.match(REGEX_PASSWORD, p):
                self._send_html(render_register_page(
                    message_type="error",
                    message_text="Wrong: Password too weak.",
                    full_name_val=html.escape(fn),
                    activity_val=html.escape(act),
                    username_val=html.escape(u)
                ))
                return



            try:
                DatabaseManager.create_user_db(u, p, fn, act)
                self._redirect("/?registered=1")
            except mysql.connector.Error:
                self._redirect("/register", "msg", "Wrong: Username already exists.")
            return

        if path == "/logout":
            self.send_response(302)
            self._clear_session()
            self.send_header("Location", "/?logout=1")
            self.end_headers()
            return

        if not self._get_session():
            self._redirect("/")
            return

        if path == "/add":

            name = fields.get("athlete_name_uats", "").strip()

            if not re.match(REGEX_FULLNAME, name):
               self._redirect("/dashboard", "msg", "Wrong: Full name must contain English letters only.")
               return
            dob = fields.get("birthdate_uats", "")
            gen = fields.get("gender_uats", "M")
            fac = fields.get("faculty_uats", "")
            sport = fields.get("sports_uats", "")
            email = fields.get("email_uats", "").strip().lower()
            if not re.fullmatch(REGEX_EMAIL, email):
              self._redirect("/dashboard", "msg", "Wrong: Invalid email format (example: name@example.com).")
              return
        
            gpa = fields.get("gpa_uats", "0")

            if not re.match(REGEX_ENGLISH_ONLY, name) or not re.match(REGEX_ENGLISH_ONLY, fac): self._redirect(
                "/dashboard", "msg", "Wrong: English characters only."); return
            try:
                if not (0.01 <= float(gpa) <= 5.0): raise ValueError
            except:
                self._redirect("/dashboard", "msg", "Wrong: GPA must be 0.01-5.0.");
                return

            try:
                if dob:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    if age < 18 or age > 100:
                        self._redirect("/dashboard", "msg", "Wrong: Athlete age must be 18-100.")
                        return
                    if dob_date > today:
                        self._redirect("/dashboard", "msg", "Wrong: Birthdate cannot be in the future.")
                        return
            except ValueError:
                self._redirect("/dashboard", "msg", "Wrong: Invalid Date");
                return

            success = DatabaseManager.create_athlete_db(name, dob, gen, fac, sport, email, gpa)
            self._redirect("/dashboard", "msg", "Add successful" if success else "Wrong: Database Error")
            return

        if path == "/update":
            aid = fields.get("athlete_id_uats", "")
            if not aid:
                self._redirect("/dashboard", "msg", "Wrong: No Athlete ID Loaded.")
                return

            name = fields.get("athlete_name_uats", "").strip()
            if not re.match(REGEX_FULLNAME, name):
               self._redirect("/dashboard", "msg", "Wrong: Full name must contain English letters only.")
               return
            dob = fields.get("birthdate_uats", "").strip()
            gen = fields.get("gender_uats", "M").strip()
            fac = fields.get("faculty_uats", "").strip()
            sport = fields.get("sports_uats", "").strip()
            email = fields.get("email_uats", "").strip().lower()
            if not re.fullmatch(REGEX_EMAIL, email):
             self._redirect("/dashboard", "msg", "Wrong: Invalid email format.")
             return
            gpa = fields.get("gpa_uats", "0").strip()

            if not (name and dob and fac and sport and email and gpa):
                self._redirect("/dashboard", "msg", "Wrong: Please fill out all fields.")
                return

            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < 18 or age > 100:
                    self._redirect("/dashboard", "msg", "Wrong: Athlete age must be between 18 and 100.")
                    return
                if dob_date > today:
                    self._redirect("/dashboard", "msg", "Wrong: Birthdate cannot be in the future.")
                    return
            except ValueError:
                self._redirect("/dashboard", "msg", "Wrong: Invalid Date.")
                return

            try:
                count = DatabaseManager.update_athlete_db(aid, name, dob, gen, fac, sport, email, gpa)
                self._redirect("/dashboard", "msg", "Update successful" if count > 0 else "Wrong: Update failed")
            except:
                self._redirect("/dashboard", "msg", "Wrong: Database Error")
            return

        if path == "/delete":
            aid = fields.get("athlete_id_uats", "")
            count = DatabaseManager.delete_athlete_db(aid)
            self._redirect("/dashboard", "msg",
                           "Delete successful" if count > 0 else "Athlete ID not found for deletion")
            return

        if path == "/update-header":
            h_id = fields.get("header_id", "1")
            system_name = fields.get("system_name", "UATS")
            logo_content = None
            if "logo" in fields and isinstance(fields["logo"], dict):
                if fields["logo"].get("filename") and fields["logo"].get("content"):
                    logo_content = fields["logo"]["content"]
            DatabaseManager.update_header_db(h_id, system_name, logo_content)
            self._redirect("/dashboard", "msg", "Header update successful")
            return

        if path == "/update-footer":
            f_id = fields.get("footer_id", "1")
            sys_name = fields.get("system_name", "").strip()
            contact_email = fields.get("contact_email", "").strip()
            if contact_email and not re.match(REGEX_EMAIL, contact_email):
              self._redirect("/dashboard", "msg", "Wrong: Invalid contact email format.")
              return
            acad_year = fields.get("academic_year", "").strip()
            contact_phone = fields.get("contact_phone", "").strip()

            if not (sys_name and acad_year):
                self._redirect("/dashboard", "msg", "Wrong: Missing footer fields.")
                return

            DatabaseManager.update_footer_db(f_id, sys_name, contact_email, acad_year, contact_phone)
            self._redirect("/dashboard", "msg", "Footer update successful")
            return

        self.send_error(404, "Action Not Found")

    def render_dashboard(self, query, load_data=None, msg=None):
        session = self._get_session()
        header_info = DatabaseManager.get_header_db()
        footer_info = DatabaseManager.get_footer_db()

        h_name = header_info[1] if header_info else "UATS SYSTEM"
        h_id = header_info[0] if header_info else "1"

        f_id = footer_info[0] if footer_info else "1"
        f_copy = footer_info[1] if footer_info else "Copyright UATS"
        f_contact_email = footer_info[2] if footer_info and len(footer_info) > 2 else ""
        f_year = footer_info[3] if footer_info and len(footer_info) > 3 else "2026"
        f_phone = footer_info[4] if footer_info and len(footer_info) > 4 else ""

        # --- 3. SEARCH & SORT FUNCTIONS (From Requirements) ()
        def bubble_sort(data, key_index, reverse=False):
            arr = data[:]
            n = len(arr)
            for i in range(n):
                for j in range(0, n - i - 1):
                    val1 = arr[j][key_index] if arr[j][key_index] is not None else ""
                    val2 = arr[j + 1][key_index] if arr[j + 1][key_index] is not None else ""

                    if key_index in [0, 7]:
                        val1 = float(val1) if val1 else 0.0
                        val2 = float(val2) if val2 else 0.0
                    else:
                        val1 = str(val1).lower()
                        val2 = str(val2).lower()

                    if (val1 > val2) != reverse:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
            return arr

        def binary_search(data, key_index, value):
            low = 0
            high = len(data) - 1
            value = value.lower()
            results = []
            while low <= high:
                mid = (low + high) // 2
                mid_val = str(data[mid][key_index]).lower() if data[mid][key_index] else ""

                if value in mid_val:
                    left = mid
                    while left >= 0 and value in (str(data[left][key_index]).lower() if data[left][key_index] else ""):
                        if data[left] not in results: results.append(data[left])
                        left -= 1
                    right = mid + 1
                    while right < len(data) and value in (
                    str(data[right][key_index]).lower() if data[right][key_index] else ""):
                        if data[right] not in results: results.append(data[right])
                        right += 1
                    break
                elif value < mid_val:
                    high = mid - 1
                else:
                    low = mid + 1
            return results

        # --- EXECUTE FETCH, SEARCH, AND SORT 
        rows = DatabaseManager.get_all_athletes_db()
        search_q = query.get("search", [""])[0]
        sort_col = query.get("sort", ["id"])[0]
        sort_ord = query.get("order", ["asc"])[0]

        key_map = {"id": 0, "name": 1, "gpa": 7}
        idx = key_map.get(sort_col, 0)
        reverse_sort = (sort_ord == "desc")

        if search_q:
            # MAGIC TRICK: We create a temporary list that puts the last name first.
            # This allows your REQUIRED binary_search to find it flawlessly.
            search_data = []
            for r in rows:
                name_parts = str(r[1]).split()
                # Add original row
                search_data.append(list(r) + [r])
                # Add permuted row so binary search hits the last name
                for i in range(1, len(name_parts)):
                    permuted_name = " ".join(name_parts[i:] + name_parts[:i])
                    permuted_row = list(r)
                    permuted_row[1] = permuted_name
                    search_data.append(permuted_row + [r])

            # Sort our special list alphabetically
            search_data = bubble_sort(search_data, 1, reverse=False)

            # Use ONLY the required binary search
            raw_results = binary_search(search_data, 1, search_q)

            # Extract the real rows back out
            seen_ids = set()
            rows = []
            for res in raw_results:
                orig_row = res[-1]
                if orig_row[0] not in seen_ids:
                    rows.append(orig_row)
                    seen_ids.add(orig_row[0])

        rows = bubble_sort(rows, idx, reverse=reverse_sort)

        def format_date_display(raw):
            if not raw:
                return ""
            try:
                if isinstance(raw, (datetime,)):
                    d = raw.date()
                elif isinstance(raw, date):
                    d = raw
                else:
                    d = datetime.strptime(str(raw)[:10], '%Y-%m-%d').date()
                return d.strftime('%d/%m/%Y')
            except Exception:
                try:
                    return str(raw)
                except:
                    return ""

        today = date.today()

        def safe_date(y, m, d):
            try:
                return date(y, m, d)
            except ValueError:
                return date(y, m, 28)

        min_dob = safe_date(today.year - 100, today.month, today.day)
        max_dob = today
        min_dob_iso = min_dob.isoformat()
        max_dob_iso = max_dob.isoformat()

        msg_html = ""
        url_msg = query.get("msg", [""])[0]
        if url_msg:
            m_type = "error" if "Wrong" in url_msg or "not found" in url_msg else "success"
            msg_html = f"<div class='message-box {'msg-success' if m_type == 'success' else 'msg-error'}'>{url_msg}</div>"
        if msg:
            msg_html = f"<div class='message-box {'msg-success' if msg[1] == 'success' else 'msg-error'}'>{msg[0]}</div>"

        table_rows = []
        if search_q and len(rows) == 0:
            table_rows.append(
                "<tr><td colspan='8' style='text-align:center; padding:30px; color:#f44336; font-weight:bold; letter-spacing:1px;'>it is not available, search by only name </td></tr>")
        else:
            for r in rows:
                dob_display = format_date_display(r[2])
                table_rows.append(
                    f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{dob_display}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td><td class='col-gpa'>{r[7]}</td></tr>")
        table_html = "".join(table_rows)

        l_id = l_name = l_gen = l_fac = l_spo = l_eml = l_gpa = ""
        l_dob_iso = ""
        l_dob_display = ""
        if load_data:
            l_id = load_data[0]
            l_name = load_data[1]
            try:
                if isinstance(load_data[2], (datetime,)):
                    dob_date = load_data[2].date()
                elif isinstance(load_data[2], date):
                    dob_date = load_data[2]
                else:
                    dob_date = datetime.strptime(str(load_data[2])[:10], '%Y-%m-%d').date()
                l_dob_iso = dob_date.isoformat()
                l_dob_display = dob_date.strftime('%d/%m/%Y')
            except Exception:
                l_dob_iso = ""
                l_dob_display = str(load_data[2]) if load_data[2] else ""
            l_gen = load_data[3]
            l_fac = load_data[4]
            l_spo = load_data[5]
            l_eml = load_data[6]
            l_gpa = load_data[7]

        logo_img_tag = ""
        if header_info and len(header_info) > 2 and header_info[2]:
            b64 = base64.b64encode(header_info[2]).decode('utf-8')
            logo_img_tag = f"<img class='header-logo' src='data:image/png;base64,{b64}' alt='Logo'>"
        elif os.path.exists(LOGO_FILENAME):
            logo_img_tag = f"<img class='header-logo' src='/logo.png' alt='Logo'>"

        welcome_html = f"<div class='welcome-section'>Welcome, <strong>{session['full_name']}</strong></div>"

        # Check if we should disable the update form
        update_disabled = "disabled" if not l_id else ""
        update_style = "opacity:0.4; pointer-events:none;" if not l_id else ""
        html = f"""
        <!DOCTYPE html>
        <html lang="en-GB">
        <head>
            <meta charset="UTF-8">
            <title>{h_name} - Dashboard</title>
            <link rel="icon" href="/logo.png" />
            {FrontendAssets.CSS_MAIN}
            {FrontendAssets.CSS_ANIMATIONS}
            <script>
            // Helper function to update the visible text input when the invisible date input changes
            function updateDisplay(dateInput) {{
                const visibleInput = dateInput.previousElementSibling;
                if (!dateInput.value) {{
                    visibleInput.value = "";
                }} else {{
                    const d = new Date(dateInput.value);
                    if (!isNaN(d.getTime())) {{
                        const day = String(d.getDate()).padStart(2, '0');
                        const month = String(d.getMonth() + 1).padStart(2, '0');
                        const year = d.getFullYear();
                        visibleInput.value = `${{day}}/${{month}}/${{year}}`;
                    }}
                }}
            }}
            </script>
        </head>
        <body>
            <div class="ambient"><div class="shimmer"></div><div class="particles"></div></div>
            <div class="header-bar">
                <div class="header-left">{logo_img_tag}<h1 class="uats-logo" style="margin:0; font-size:24px; color:#f0f0f0;">{h_name}</h1></div>
                <form action="/logout" method="POST" style="margin:0;"><button class="btn-nav btn-danger" style="height:34px; padding: 0 20px;">LOGOUT</button></form>
            </div>

            {welcome_html}

            {msg_html}

            <div class="glass-card">
                <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:15px; flex-wrap:wrap; gap:10px;">
                    <div class="section-title" style="margin:0;">ATHLETE LIST</div>
                    <form method="GET" action="/dashboard" style="display:flex; gap:5px;">
                        <input type="text" name="search" placeholder="Search Name " value="{search_q}" style="width:200px; padding:6px;">
                        <button class="btn-nav btn-purple">SEARCH</button>
                        <a href="/dashboard" class="btn-nav" style="display:flex; align-items:center;">RESET</a>
                    </form>
                </div>
<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px;">
    <a href="/dashboard?sort=id&order=asc" class="btn-nav">SORT ID &uarr;</a>
    <a href="/dashboard?sort=id&order=desc" class="btn-nav">SORT ID &darr;</a>
    <a href="/dashboard?sort=name&order=desc" class="btn-nav">SORT NAME &uarr;</a>
    <a href="/dashboard?sort=name&order=asc" class="btn-nav">SORT NAME &darr;</a>
    <a href="/dashboard?sort=gpa&order=asc" class="btn-nav">SORT GPA &uarr;</a>
    <a href="/dashboard?sort=gpa&order=desc" class="btn-nav">SORT GPA &darr;</a>
</div>
                <div style="overflow-x:auto;"><table><thead><tr><th>ID_uats</th><th>NAME_uats</th><th>BIRTHDATE_uats</th><th>GENDER_uats</th><th>FACULTY_uats</th><th>SPORT_uats</th><th>EMAIL_uats</th><th class="col-gpa">GPA_uats</th></tr></thead><tbody>{table_html}</tbody></table></div>
                <div style="margin-top:10px; font-size:12px; color:#666;">Total Records: {len(rows)}</div>
            </div>
            <div class="glass-card">
                <div class="section-title">ADD NEW ATHLETE</div>
                <form action="/add" method="POST" class="field-row">
                    <div class="field-group"><label>Name_uats</label><input type="text" name="athlete_name_uats"
       required
       pattern="^[A-Za-z\s]+$"
       title="English letters only (no numbers or symbols)"></div>

                    <div class="field-group" style="position:relative;">
                        <label>Birthdate_uats</label>
                        <div style="position:relative; width:100%; height:42px;">
                            <input type="text" placeholder="dd/mm/yyyy" readonly style="position:absolute; inset:0; z-index:1; background:rgba(0,0,0,0.3); color:white; border:1px solid #7b3fb0; border-radius:6px; padding:10px;">
                            <input type="date" name="birthdate_uats" required max="{max_dob_iso}" min="{min_dob_iso}"
                                   style="position:absolute; inset:0; z-index:2; opacity:0; cursor:pointer; width:100%; height:100%;"
                                   onchange="updateDisplay(this)" oninput="updateDisplay(this)">
                        </div>
                    </div>

                    <div class="field-group"><label>Gender_uats</label><select name="gender_uats"><option value="M">Male</option><option value="F">Female</option></select></div>
                    <div class="field-group"><label>Faculty_uats</label><input type="text" name="faculty_uats" required pattern="^[a-zA-Z0-9\s.,!?'()-]*$" title="English characters only"></div>
                    <div class="field-group"><label>Sport_uats</label><input type="text" name="sports_uats" required></div>
                    <div class="field-group"><label>Email_uats</label><input type="email"
       name="email_uats"
       required
       title="Example: name@example.com"></div>
                    <div class="field-group"><label>GPA_uats</label><input type="number" step="0.01" min="0.01" max="5" name="gpa_uats" required placeholder="0.01 - 5.00"></div>
                    <button class="btn-nav btn-purple" style="height:38px; margin-top: 22px;">ADD ATHLETE</button>
                </form>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; width: 100%;">
                <div class="glass-card" style="margin:0;">
                    <div class="section-title" style="font-size: 0.9em;">MANAGE DATA BY ID</div>
                    <form action="/load" method="GET" class="field-row" style="margin-bottom:20px;">
                        <input type="text" name="athlete_id_uats" placeholder="Enter Athlete ID to Load" style="flex:2;" required>
                        <button class="btn-nav btn-purple" style="flex:1;">LOAD DATA TO UPDATE</button>
                    </form>
                    <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:15px 0;">
                    <form action="/delete" method="POST" class="field-row" onsubmit="return confirmDelete(this);">
                        <input type="text" name="athlete_id_uats" placeholder="Enter Athlete ID to Delete" style="flex:2;" required>
                        <button class="btn-nav btn-danger" style="flex:1;">DELETE </button>
                    </form>
                </div>
                <div class="glass-card" style="margin:0; grid-column: span 2;"> <div class="section-title">UPDATE ATHLETE DATA (Put ID on the left box) </div>
                    <form action="/update" method="POST" id="updateForm">
                    <fieldset {update_disabled} style="border:none; padding:0; margin:0; width:100%; {update_style}">
                        <div class="field-row">
                            <div class="field-group"><label>ID</label><input type="number"
       name="athlete_id_uats"
       value="{l_id}"
       readonly
       pattern="^[A-Za-z\s]+$"
       title="English letters only (no numbers or symbols)"></div>
                            <div class="field-group"><label>Name_uats</label><input type="text" name="athlete_name_uats" value="{l_name}" pattern="^[a-zA-Z0-9\s.,!?'()-]*$"><div class="inline-error" data-for="athlete_name_uats"></div></div>

                            <div class="field-group" style="position:relative;">
                                <label>Birthdate_uats</label>
                                <div style="position:relative; width:100%; height:42px;">
                                    <input type="text" value="{l_dob_display}" placeholder="dd/mm/yyyy" readonly style="position:absolute; inset:0; z-index:1; background:rgba(0,0,0,0.3); color:white; border:1px solid #7b3fb0; border-radius:6px; padding:10px;">
                                    <input type="date" name="birthdate_uats" value="{l_dob_iso}" max="{max_dob_iso}" min="{min_dob_iso}"
                                           style="position:absolute; inset:0; z-index:2; opacity:0; cursor:pointer; width:100%; height:100%;"
                                           onchange="updateDisplay(this)" oninput="updateDisplay(this)">
                                </div>
                                <div class="inline-error" data-for="birthdate_uats"></div>
                            </div>

                            <div class="field-group"><label>Gender_uats</label><select name="gender_uats"><option value="M" {"selected" if l_gen == 'M' else ""}>Male</option><option value="F" {"selected" if l_gen == 'F' else ""}>Female</option></select></div>
                            <div class="field-group"><label>Faculty_uats</label><input type="text" name="faculty_uats" value="{l_fac}"><div class="inline-error" data-for="faculty_uats"></div></div>
                            <div class="field-group"><label>Sport_uats</label><input type="text" name="sports_uats" value="{l_spo}"><div class="inline-error" data-for="sports_uats"></div></div>
                            <div class="field-group"><label>Email_uats</label><input type="email"
       name="email_uats"
       value="{l_eml}"
       required
       title="Example: name@example.com"></div></div>
                            <div class="field-group"><label>GPA_uats</label><input type="number" step="0.01" min="0" max="5" name="gpa_uats" value="{l_gpa}"><div class="inline-error" data-for="gpa_uats"></div></div>
                            <div style="width:100%; margin-top:10px; display:flex; justify-content:flex-end;"><button type="submit" class="btn-nav btn-purple" style="padding:10px 40px;">CONFIRM UPDATE</button></div>
                        </div>
                    </fieldset>
                    </form>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; max-width: 1400px; margin: 20px auto; width: 100%;">

                <div class="glass-card" style="margin:0;">
                    <div class="section-title">UPDATE HEADER</div>
                    <form action="/update-header" method="POST" enctype="multipart/form-data">
                        <input type="hidden" name="header_id" value="{h_id}">
                        <div class="field-group" style="margin-bottom:15px;"><label>System_Name_uats</label><input type="text" name="system_name" value="{h_name}" required></div>
                        <div class="field-group" style="margin-bottom:15px;"><label>Logo_uats (Upload PNG/JPG)</label><input type="file" name="logo" accept="image/png,image/jpeg" style="padding:8px;"></div>
                        <button class="btn-nav btn-purple">SAVE HEADER CONFIG</button>
                    </form>
                </div>

                <div class="glass-card" style="margin:0;">
                    <div class="section-title">UPDATE FOOTER </div>
                    <form action="/update-footer" method="POST">
                        <input type="hidden" name="footer_id" value="{f_id}">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                            <div class="field-group"><label>System_Name_uats</label><input type="text" name="system_name" value="{f_copy}"></div>
                            <div class="field-group"><label>Academic_Year_uats</label><input type="text" name="academic_year" value="{f_year}"></div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:10px;">
                            <div class="field-group">
    <label>Contact_Email_uats</label>
   <input type="email"
       name="contact_email"
       value="{f_contact_email}"
       required
       title="Example: name@example.com">
</div>
                            <div class="field-group"><label>Contact_Phone_uats</label><input type="text" name="contact_phone" value="{f_phone}"></div>
                        </div>
                        <button class="btn-nav btn-purple" style="margin-top:15px;">SAVE FOOTER CONFIG</button>
                    </form>
                </div>

            </div>
            <footer><div class="footer-content"><div class="footer-copy">{f_copy}</div><div class="footer-info">© {f_year} UATS System. All rights reserved. {f_contact_email and (' | ' + f_contact_email) or ''} {f_phone and (' | ' + f_phone) or ''}</div></div></footer>
            <div id="customModal" class="modal-overlay">
                <div class="modal-box">
                    <div class="section-title" style="border:none; margin-bottom:15px; text-align:center;">CONFIRM DELETION</div>
                    <p style="color:#cfcfcf; margin-bottom:10px;">Are you sure you want to permanently delete Athlete ID <span id="delIdDisplay" style="color:var(--yellow-main); font-weight:bold; font-size:1.1em;"></span>?</p>
                    <p style="font-size:12px; color:#888; margin-bottom:25px;">This action cannot be undone.</p>
                    <div style="display:flex; justify-content:center; gap:15px;">
                       <button class="btn-nav" style="background:transparent; border:1px solid rgba(255,255,255,0.2); color:#cfcfcf; width:auto; padding:8px 20px;" onclick="closeModal()">CANCEL</button>
                       <button class="btn-nav btn-danger" style="width:auto; padding:8px 20px;" onclick="executeDelete()">CONFIRM DELETE</button>
                    </div>
                </div>
            </div>
            <script>
                let formToSubmit = null;
                function confirmDelete(form) {{
                    const idVal = form.athlete_id_uats.value;
                    if (!idVal) {{ alert("Please enter an ID first."); return false; }}
                    formToSubmit = form;
                    document.getElementById('delIdDisplay').innerText = idVal;
                    document.getElementById('customModal').style.display = 'flex';
                    return false;
                }}
                function closeModal() {{ document.getElementById('customModal').style.display = 'none'; formToSubmit = null; }}
                function executeDelete() {{ if(formToSubmit) {{ formToSubmit.submit(); }} }}

                document.addEventListener('DOMContentLoaded', function() {{
                    const updateForm = document.getElementById('updateForm');
                    if (!updateForm) return;

                    function clearErrors() {{
                        updateForm.querySelectorAll('.inline-error').forEach(el => el.textContent = '');
                    }}

                    function setError(name, message) {{
                        const el = updateForm.querySelector(`.inline-error[data-for="${{name}}"]`);
                        if (el) el.textContent = message;
                    }}

                    updateForm.addEventListener('submit', function (e) {{
                        clearErrors();
                        const requiredNames = [
                            'athlete_name_uats',
                            'faculty_uats',
                            'sports_uats',
                            'email_uats',
                            'gpa_uats'
                        ];
                        let firstInvalid = null;

                        for (const name of requiredNames) {{
                            const field = updateForm.querySelector(`[name="${{name}}"]`);
                            if (!field || (typeof field.value === 'string' && field.value.trim() === '')) {{
                                e.preventDefault();
                                setError(name, 'Please fill out this field');
                                if (!firstInvalid) firstInvalid = field;
                            }}
                        }}

                        // NOTE: Date is now checked via the hidden field logic, which returns 'yyyy-mm-dd'
                        const bdField = updateForm.querySelector('[name="birthdate_uats"]');
                        if (bdField && bdField.value) {{
                            const val = bdField.value;
                            // The hidden input always returns yyyy-mm-dd
                            const parts = val.split('-');
                            if (parts.length === 3) {{
                                const y = parseInt(parts[0],10), m = parseInt(parts[1],10)-1, d = parseInt(parts[2],10);
                                const picked = new Date(y, m, d);
                                const today = new Date();
                                picked.setHours(0,0,0,0);
                                today.setHours(0,0,0,0);
                                if (picked > today) {{
                                    e.preventDefault();
                                    setError('birthdate_uats', 'Birthdate cannot be in the future');
                                    if (!firstInvalid) firstInvalid = bdField;
                                }} else {{
                                    let age = today.getFullYear() - picked.getFullYear();
                                    const mDiff = today.getMonth() - picked.getMonth();
                                    const dDiff = today.getDate() - picked.getDate();
                                    if (mDiff < 0 || (mDiff === 0 && dDiff < 0)) age--;
                                    if (age < 18 || age > 100) {{
                                        e.preventDefault();
                                        setError('birthdate_uats', 'Age must be between 18 and 100');
                                        if (!firstInvalid) firstInvalid = bdField;
                                    }}
                                }}
                            }} else {{
                                e.preventDefault();
                                setError('birthdate_uats', 'Invalid date format');
                                if (!firstInvalid) firstInvalid = bdField;
                            }}
                        }} else {{
                            e.preventDefault();
                            setError('birthdate_uats', 'Please select a date');
                            if (!firstInvalid) firstInvalid = bdField;
                        }}

                        if (firstInvalid) {{
                            firstInvalid.focus();
                        }}
                    }}, false);
                }});
            </script>
        </body>
        </html>
        """
        self._send_html(html)

# =================================================================================================
# SECTION 6: MAIN EXECUTION ENTRY POINT
# =================================================================================================

def run_server():
    conn = DatabaseManager.get_connection()
    db_status = "Connected" if conn else "Failed"
    if conn:
        conn.close()

    server_address = ("", SERVER_PORT)
    httpd = http.server.HTTPServer(server_address, UATSServerHandler)

    url = f"http://127.0.0.1:{SERVER_PORT}/"
    print(f"UATS Server running at {url} (Database: {db_status}) - Press Ctrl+C to stop.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


def run_web():
    import webbrowser
    url = f"http://127.0.0.1:{SERVER_PORT}/"
    webbrowser.open(url)
    run_server()


def run_cli():
    session = Session()
    menu_loop(session)


if __name__ == "__main__":
    while True:
        print("\nChoose mode:")
        print("1) CLI (Terminal)")
        print("2) WEB (Browser)")
        mode = input("Enter 1 or 2: ").strip()

        if mode == "1":
            run_cli()
            break
        elif mode == "2":
            run_web()
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.\n")











  
