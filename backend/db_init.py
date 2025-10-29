import sqlite3
from sqlite3 import Error
import queue
import threading
import logging
import hashlib
import random

# Behtar logging ke liye setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """
    Ek thread-safe database manager jo connection pooling ka istemal karta hai.
    Yeh high concurrency (ek saath kai users) ke liye design kiya gaya hai.
    Ismein ab advanced event registration system bhi hai.
    """
    def __init__(self, db_file, pool_size=5):
        self.db_file = db_file
        self.pool_size = pool_size
        self.pool = queue.Queue(maxsize=self.pool_size)
        self._lock = threading.Lock()

        try:
            for _ in range(self.pool_size):
                conn = self._create_connection()
                self.pool.put(conn)
            logging.info(f"{self.pool_size} connections ka pool safaltapoorvak banaya gaya.")
            self._setup_database_schema()
            self._insert_initial_data()
        except Error as e:
            logging.error(f"Database pool banate waqt error aaya: {e}")
            raise

    def _create_connection(self):
        """ Ek naya database connection banata hai. """
        try:
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            conn.execute("PRAGMA foreign_keys = 1") # Foreign key support enable karein
            return conn
        except Error as e:
            logging.error(f"Connection banate waqt error: {e}")
            return None

    def get_connection(self):
        """ Pool se ek connection leta hai. """
        return self.pool.get()

    def return_connection(self, conn):
        """ Connection ko wapas pool mein daalta hai. """
        self.pool.put(conn)

    def execute_query(self, query, params=(), many=False):
        """
        Ek query ko execute karne ke liye ek context manager.
        Yeh connection ko automatically pool se leta aur wapas karta hai.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        last_id = None
        try:
            if many:
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            logging.info("Query safaltapoorvak execute hui.")
        except Error as e:
            logging.error(f"Query execute karte waqt error: {e}")
            conn.rollback() # Galti hone par changes ko undo karein
        finally:
            self.return_connection(conn)
        return last_id

    def execute_read_query(self, query, params=()):
        """
        Data padhne ke liye (SELECT) ek query execute karta hai.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        result = None
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            logging.error(f"Read query execute karte waqt error: {e}")
            return None
        finally:
            self.return_connection(conn)
            
    def _create_table(self, create_table_sql):
        """ Helper function to create a table """
        self.execute_query(create_table_sql)

    def _setup_database_schema(self):
        """ Sabhi zaroori tables ke liye schema banayein """
        with self._lock:
            logging.info("Database schema setup kiya ja raha hai...")
            # Puraane tables
            self._create_table("CREATE TABLE IF NOT EXISTS faculty (id integer PRIMARY KEY, name text NOT NULL, qualification text, department text, subjects text, email text, linkedin_url text, image_url text);")
            self._create_table("CREATE TABLE IF NOT EXISTS events (id integer PRIMARY KEY, name text NOT NULL, category text NOT NULL, event_date text);")
            self._create_table("CREATE TABLE IF NOT EXISTS tiro_members (id integer PRIMARY KEY, name text NOT NULL, designation text NOT NULL, quote text, linkedin_url text, email text, image_url text);")
            self._create_table("CREATE TABLE IF NOT EXISTS subjects (id integer PRIMARY KEY, name text NOT NULL, faculty_name text, description text, branch_tags text, semester integer);")
            self._create_table("CREATE TABLE IF NOT EXISTS college_info (id integer PRIMARY KEY, info_type text NOT NULL, content text NOT NULL, image_url text);")
            
            # --- Naye Registration Tables ---
            # Har registration ki main entry ke liye
            sql_create_registrations_table = """CREATE TABLE IF NOT EXISTS event_registrations (
                                                id INTEGER PRIMARY KEY,
                                                event_id INTEGER NOT NULL,
                                                registration_type TEXT NOT NULL CHECK(registration_type IN ('individual', 'team')),
                                                registration_code TEXT UNIQUE NOT NULL, -- Yahan PID ya TID store hoga
                                                primary_registrant_name TEXT NOT NULL,
                                                aadhaar_number_hash TEXT NOT NULL, -- Asli Aadhaar no. nahi, sirf hash store karein
                                                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                FOREIGN KEY (event_id) REFERENCES events (id)
                                            );"""
            # Team registration ke members ke liye
            sql_create_team_members_table = """CREATE TABLE IF NOT EXISTS team_members (
                                                id INTEGER PRIMARY KEY,
                                                registration_id INTEGER NOT NULL,
                                                member_name TEXT NOT NULL,
                                                FOREIGN KEY (registration_id) REFERENCES event_registrations (id)
                                            );"""
            
            self._create_table(sql_create_registrations_table)
            self._create_table(sql_create_team_members_table)
            logging.info("Sabhi tables safaltapoorvak banaye gaye.")

    def _insert_initial_data(self):
        """ Shuruaati data tables mein daalein, agar zaroori ho """
        with self._lock:
            if not self.execute_read_query("SELECT * FROM faculty WHERE id=1"):
                logging.info("Shuruaati data daala ja raha hai...")
                # Puraana data...
                faculty_data = [(1, 'Dr. Anuj Kumar', 'Ph.D, M.Tech (HOD, CSE)', 'CSE', 'Engineering Maths, Data Structures', 'anuj.k@srms.ac.in', '#', '...'), (2, 'Prof. Shweta Sharma', 'M.Tech (CSE)', 'CSE', 'C Programming, Web Tech', 'shweta.s@srms.ac.in', '#', '...')]
                self.execute_query("INSERT INTO faculty (id, name, qualification, department, subjects, email, linkedin_url, image_url) VALUES (?,?,?,?,?,?,?,?)", faculty_data, many=True)
                events_data = [(1, 'CodeClash 2025', 'Tech', '2025-08-15'), (2, 'RoboWars', 'Tech', '2025-09-01')]
                self.execute_query("INSERT INTO events (id, name, category, event_date) VALUES (?,?,?,?)", events_data, many=True)
                
                # --- Naya Sample Registration Data ---
                # 1. Individual Registration
                aadhaar_hash_1 = hashlib.sha256("123456789012".encode()).hexdigest()
                pid = f"PID-{random.randint(10000, 99999)}"
                self.execute_query("INSERT INTO event_registrations (event_id, registration_type, registration_code, primary_registrant_name, aadhaar_number_hash) VALUES (?, ?, ?, ?, ?)",
                                   (1, 'individual', pid, 'Amit Kumar', aadhaar_hash_1))

                # 2. Team Registration
                aadhaar_hash_2 = hashlib.sha256("987654321098".encode()).hexdigest()
                tid = f"TID-{random.randint(1000, 9999)}"
                team_reg_id = self.execute_query("INSERT INTO event_registrations (event_id, registration_type, registration_code, primary_registrant_name, aadhaar_number_hash) VALUES (?, ?, ?, ?, ?)",
                                   (2, 'team', tid, 'Sunita Sharma (Team Leader)', aadhaar_hash_2))
                
                # Team members daalein
                if team_reg_id:
                    team_members = [
                        (team_reg_id, 'Sunita Sharma'),
                        (team_reg_id, 'Rajesh Verma'),
                        (team_reg_id, 'Priya Gupta')
                    ]
                    self.execute_query("INSERT INTO team_members (registration_id, member_name) VALUES (?, ?)", team_members, many=True)

                logging.info("Shuruaati data safaltapoorvak daal diya gaya hai.")
            else:
                logging.info("Database mein pehle se data hai. Initial data nahi daala gaya.")

    def close_all_connections(self):
        """ Pool ke sabhi connections ko band karein """
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
        logging.info("Pool ke sabhi connections band kar diye gaye hain.")


def main():
    """ Main function jo database ko setup aur test karta hai """
    database_file = "srms_portal_prod.db"
    
    try:
        db_manager = DatabaseManager(database_file)

        logging.info("\n--- Sabhi Registrations ---")
        all_regs = db_manager.execute_read_query("""
            SELECT r.registration_code, e.name, r.registration_type, r.primary_registrant_name
            FROM event_registrations r
            JOIN events e ON r.event_id = e.id
        """)
        if all_regs:
            for reg in all_regs:
                print(f"Code: {reg[0]}, Event: {reg[1]}, Type: {reg[2]}, Registrant: {reg[3]}")
                # Agar team hai to members dikhayein
                if reg[2] == 'team':
                    team_members = db_manager.execute_read_query("""
                        SELECT m.member_name FROM team_members m 
                        JOIN event_registrations r ON m.registration_id = r.id 
                        WHERE r.registration_code = ?
                    """, (reg[0],))
                    if team_members:
                        member_names = [m[0] for m in team_members]
                        print(f"    Team Members: {', '.join(member_names)}")

        db_manager.close_all_connections()

    except Error as e:
        logging.error(f"Application shuru karte waqt ek anapratyashit error aaya: {e}")

if __name__ == '__main__':
    main()
